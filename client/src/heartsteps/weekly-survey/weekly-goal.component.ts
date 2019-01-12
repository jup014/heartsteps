import { Component, Output, EventEmitter, Input } from '@angular/core';

import { LoadingService } from '@infrastructure/loading.service';
import { Week } from './week.model';

@Component({
  selector: 'heartsteps-weekly-goal',
  templateUrl: './weekly-goal.component.html',
  inputs: ['week', 'call-to-action']
})
export class WeeklyGoalComponent {

    @Input('call-to-action') cta:string = "Set goal";
    @Output() saved = new EventEmitter<boolean>();

    public minutes:number;
    public confidence:number;
    private _week:Week;

    constructor(
        private loadingService:LoadingService
    ) {}

    @Input()
    set week(week:Week) {
        if(week) {
            this._week = week;
            this.minutes = week.goal;
            this.confidence = week.confidence;
        }
    }

    save() {
        this.loadingService.show("Saving goal");
        this._week.setGoal(this.minutes, this.confidence)
        .then(() => {
            this.loadingService.dismiss();
            this.saved.emit();
        })
    }
    

}
