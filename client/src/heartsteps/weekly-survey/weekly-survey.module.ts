import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { InfrastructureModule } from '@infrastructure/infrastructure.module';
import { IonicPageModule } from 'ionic-angular';
import { ReflectionTimeService } from './reflection-time.service';
import { WeeklyReflectionTimePage } from './weekly-reflection-time.page';
import { WeekService } from './week.service';
import { WeeklyGoalComponent } from './weekly-goal.component';
import { WeeklySurveyService } from './weekly-survey.service';
import { FormModule } from '@infrastructure/form/form.module';

@NgModule({
    imports: [
        InfrastructureModule,
        FormModule,
        BrowserModule,
        IonicPageModule.forChild(WeeklyGoalComponent),
        IonicPageModule.forChild(WeeklyReflectionTimePage),
    ],
    providers: [
        ReflectionTimeService,
        WeekService,
        WeeklySurveyService
    ],
    declarations: [
        WeeklyReflectionTimePage,
        WeeklyGoalComponent
    ],
    exports: [
        WeeklyReflectionTimePage,
        WeeklyGoalComponent
    ]
})
export class WeeklySurveyModule {}
