import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';

import { IonicApp, IonicModule } from 'ionic-angular';
import { SplashScreen } from '@ionic-native/splash-screen';
import { StatusBar } from '@ionic-native/status-bar';

import { HeartstepsWebsite } from './app.component';

import { WelcomePageModule } from '@pages/welcome/welcome.module';
import { OnboardPageModule } from '@pages/onboard/onboard.module';
import { HomePageModule } from '@pages/home/home.module';
import { NotificationsModule as NotificationsPageModule } from '@pages/notifications/notifications.module';
import { NotificationsModule } from '@heartsteps/notifications/notifications.module';
import { WeeklySurveyModule } from '@pages/weekly-survey/weekly-survey.module';
import { MorningSurveyPageModule } from '@pages/morning-survey/morning-survey.module';
import { CurrentWeekModule } from '@heartsteps/current-week/current-week.module';
import { HeartstepsInfrastructureModule } from '@infrastructure/heartsteps/heartsteps.module';
import { AnalyticsService } from '@infrastructure/heartsteps/analytics.service';

const appRoutes:Routes = [{
  path: '',
  redirectTo: '/home/dashboard',
  pathMatch: 'full'
}]

@NgModule({
  declarations: [
    HeartstepsWebsite
  ],
  imports: [
    WelcomePageModule,
    CurrentWeekModule,
    OnboardPageModule,
    HomePageModule,
    HeartstepsInfrastructureModule,
    NotificationsModule,
    NotificationsPageModule,
    WeeklySurveyModule,
    MorningSurveyPageModule,
    BrowserAnimationsModule,
    IonicModule.forRoot(HeartstepsWebsite),
    RouterModule.forRoot(
      appRoutes,
      {
        useHash: true
      }
    )
  ],
  bootstrap: [IonicApp],
  entryComponents: [
    HeartstepsWebsite
  ],
  providers: [
    StatusBar,
    SplashScreen,
    AnalyticsService
  ]
})
export class AppModule {}
