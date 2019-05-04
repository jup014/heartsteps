import { Injectable } from "@angular/core";
import { Week } from "./week.model";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { WeekSerializer } from "./week.serializer";

@Injectable()
export class WeekService {
    
    constructor(
        private heartstepsServer: HeartstepsServer,
        private weekSerializer: WeekSerializer
    ){}

    getWeek(weekId:string):Promise<Week> {
        return this.heartstepsServer.get('weeks/'+weekId)
        .then((data:any) => {
            return this.deserializeWeek(data);
        });
    }

    public getWeekSurvey(week: Week): Promise<any> {
        return this.heartstepsServer.get('weeks/' + week.id + '/survey')
        .then((response) => {
            return response;
        });
    }

    public submitWeekSurvey(week: Week, values: any): Promise<boolean> {
        return this.heartstepsServer.post('weeks/' + week.id + '/survey', values)
        .then(() => {
            return true;
        });
    }

    setWeekGoal(week:Week, minutes:number, confidence:number):Promise<Week> {
        return this.heartstepsServer.post('weeks/' + week.id, {
            goal: minutes,
            confidence: confidence
        })
        .then(() => {
            week.goal = minutes;
            week.confidence = confidence;
            return week;
        });
    }

    public getCurrentWeek():Promise<Week> {
        return this.heartstepsServer.get('weeks/current')
        .then((data:any) => {
            return this.deserializeWeek(data);
        });
    }

    public getNextWeek():Promise<Week> {
        return this.heartstepsServer.get('weeks/next')
        .then((data:any) => {
            return this.deserializeWeek(data);
        });
    }

    public deserializeWeek(data:any):Week {
        return this.weekSerializer.deserialize(data);
    }

    public serializeWeek(week:Week):any {
        return this.weekSerializer.serialize(week);
    }

}