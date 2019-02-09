import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { Injectable } from "@angular/core";
import { StorageService } from "@infrastructure/storage.service";
import { BehaviorSubject } from "rxjs";

const storageKey: string = 'activity-types';

export class ActivityType {
    title: string;
    name: string;
}

@Injectable()
export class ActivityTypeService {

    public activityTypes:BehaviorSubject<Array<ActivityType>>;

    constructor(
        private heartstepsServer: HeartstepsServer,
        private storage: StorageService
    ) {
        this.activityTypes = new BehaviorSubject([]);
        this.getActivityTypes()
        .then((activityTypes) => {
            this.activityTypes.next(activityTypes);
        });
    }

    public load():Promise<Array<ActivityType>> {
        return this.heartstepsServer.get('activity/types')
        .then((response: Array<ActivityType>) => {
            return this.storage.set(storageKey, response);
        })
        .then(() => {
            return this.getActivityTypes();
        });
    }

    public get(type:string):Promise<ActivityType> {
        return this.getActivityTypes()
        .then((types) => {
            const filteredTypes:Array<ActivityType> = types.filter((activityType) => { 
                return activityType.name === type 
            });
            if(filteredTypes.length === 1) {
                return Promise.resolve(filteredTypes[0]);
            } else {
                return Promise.reject("No matching type");
            }
        });
    }

    public create(type:string): Promise<ActivityType> {
        return this.heartstepsServer.post('activity/types', {
            name: type
        })
        .then((data) => {
            const activityType = this.deserialize(data);
            return this.load()
            .then(() => {
                return activityType;
            })
        });
    }

    private getActivityTypes():Promise<Array<ActivityType>> {
        return this.storage.get(storageKey)
        .then((types:Array<any>) => {
            const activityTypes = this.deserializeActivityTypes(types);
            return this.sortByName(activityTypes);
        })
        .catch(() => {
            return this.load();
        });
    }

    private deserializeActivityTypes(list:Array<any>):Array<ActivityType> {
        const activityTypes:Array<ActivityType> = [];
        list.forEach((item:any) => {
            const activityType = this.deserialize(item);
            activityTypes.push(activityType);
        });
        return activityTypes;
    }

    private deserialize(data:any): ActivityType {
        const activityType = new ActivityType();
        activityType.name = data.name;
        activityType.title = data.title;
        return activityType;
    }

    private sortByName(activityTypes: Array<ActivityType>): Array<ActivityType> {
        return [...activityTypes].sort((a, b) => {
            if(a.name > b.name) return 1;
            if(a.name < b.name) return -1;
            return 0;
        });
    }
}