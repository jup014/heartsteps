import { Component, OnInit, Input, OnDestroy } from '@angular/core';
import * as moment from 'moment';
import { ActivityPlanService } from '@heartsteps/activity-plan.service';
import { Subscription } from 'rxjs';

@Component({
    selector: 'activity-plan-day',
    templateUrl: './day-plan.component.html',
    inputs: ['date']
})
export class DayPlanComponent implements OnInit, OnDestroy {

    @Input() date: Date;
    dateFormatted: string;

    activityPlanSubscription: Subscription;

    plans: Array<any> = [];

    constructor(
        private activityPlanService:ActivityPlanService
    ) {}

    ngOnInit(){
        this.dateFormatted = moment(this.date).format("dddd, M/D");

        this.activityPlanSubscription = this.activityPlanService.plans.subscribe((plans) => {
            this.filterPlans(plans);
        });
    }

    ngOnDestroy() {
        this.activityPlanSubscription.unsubscribe();
    }

    filterPlans(plans) {
        let filteredPlans = [];

        plans.forEach((plan) => {
            if(moment(this.date).format("YYYY-MM-DD") == moment(plan.date).format("YYYY-MM-DD")) {
                filteredPlans.push(plan);
            }
        })

        this.plans = filteredPlans;
    }
}
