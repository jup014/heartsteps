import { Injectable } from "@angular/core";
import { Storage } from "@ionic/storage";
import {BehaviorSubject} from 'rxjs';
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { Activity } from "@heartsteps/activity/activity.model";

const storageKey = 'activityPlans';

@Injectable()
export class ActivityPlanService {

    public plans: BehaviorSubject<Array<Activity>>

    constructor(
        private storage:Storage,
        private heartstepsServer:HeartstepsServer
    ){
        this.plans = new BehaviorSubject([]);
        this.updateSubject();
    }

    updateSubject() {
        this.loadPlans()
        .then((plans) => {
            this.plans.next(plans);
        })
    }

    createPlan(activity:Activity):Promise<Activity> {
        return this.heartstepsServer.post('/activity/plans', activity.serialize())
        .then((response:any) => {
            const activity = new Activity(response);
            return this.storeActivity(activity);
        })
        .then((activity:Activity) => {
            this.updateSubject();
            return new Activity(activity);
        })
    }

    delete(activity:Activity):Promise<boolean> {
        return Promise.resolve(true);
    }

    complete(activity:Activity):Promise<Activity> {
        return this.heartstepsServer.post('/activity/logs', {
            type: activity.type,
            start: activity.start,
            duration: activity.duration,
            vigorous: activity.vigorous,
            enjoyed: 3
        })
        .then((response:any) => {
            activity.markComplete();
            return this.storeActivity(activity);
        })
    }

    getPlans(startDate:Date, endDate:Date):Promise<boolean> {
        return this.heartstepsServer.get('activity/plans', {
            start: startDate.toISOString(),
            end: endDate.toISOString()
        })
        .then((response: Array<any>) => {
            let plans = {};
            response.forEach((plan: any) => {
                plans[plan.id] = plan;
            });
            return this.storage.set(storageKey, plans);
        })
        .then(() => {
            this.updateSubject();
            return true;
        })
    }

    private loadPlans():Promise<Array<Activity>> {
        return this.storage.get(storageKey)
        .then((plans) => {
            if (plans) {
                let activities = [];
                Object.keys(plans).forEach((planId:string) => {
                    let activity = new Activity(plans[planId]);
                    activity.id = planId;
                    activities.push(activity);
                });
                return activities;
            } else  {
                return [];
            }
        });
    }

    private storeActivity(activity:Activity):Promise<Activity> {
        return this.storage.get(storageKey)
        .then((plans) => {
            if (!plans) {
                plans = {};
            }
            plans[activity.id] = activity.serialize();
            return this.storage.set(storageKey, plans)
        })
        .then(() => {
            return activity;
        })
    }

}