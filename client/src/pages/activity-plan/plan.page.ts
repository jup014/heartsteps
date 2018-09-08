import { Component } from '@angular/core';
import { DateFactory } from '@heartsteps/date.factory';
import { ModalController } from 'ionic-angular';
import { PlanModal } from '@pages/activity-plan/plan.modal';

@Component({
    selector: 'page-plan',
    templateUrl: 'plan.page.html'
})
export class PlanPage {

    dates:Array<Date>

    constructor(
        dateFactory:DateFactory,
        private modalCtrl:ModalController
    ) {
        this.dates = dateFactory.getCurrentWeek();
    }

    addActivity(date:Date) {
        let modal = this.modalCtrl.create(PlanModal, {
            date: date
        });
        modal.present()
    }
}
