import { Component } from '@angular/core';
import { Platform } from 'ionic-angular';
import { StatusBar } from '@ionic-native/status-bar';
import { SplashScreen } from '@ionic-native/splash-screen';
import { ParticipantService, Participant } from '@heartsteps/participants/participant.service';
import { NotificationService } from './notification.service';
import { AuthorizationService } from './authorization.service';
import { AnalyticsService } from '@infrastructure/heartsteps/analytics.service';
import { Router } from '@angular/router';

@Component({
    templateUrl: 'app.html'
})
export class MyApp {

    showDashboard: boolean = false;

    constructor(
        platform: Platform,
        statusBar: StatusBar,
        splashScreen: SplashScreen,
        private participantService:ParticipantService,
        private notificationService: NotificationService,
        private authorizationService: AuthorizationService,
        private analyticsService: AnalyticsService,
        private router: Router
    ) {
        platform.ready()
        .then(() => {
            return this.analyticsService.setup();
        })
        .then(() => {
            this.participantService.participant.subscribe((participant) => {
                console.log('App component', 'got participant', participant);
                Promise.all([
                    this.setupAuthorization(participant),
                    this.setupNotifications(participant)
                ])
                .catch(() => {
                    console.log('There was an error');
                })
                .then(() => {
                    this.updateRoute(participant);
                });
            });
            return this.participantService.update();
        })
        .then(() => {
            statusBar.styleDefault();
            splashScreen.hide();
        });
    }

    private updateRoute(participant: Participant) {
        if(this.router.url === "/") {
            if(participant && participant.isSetup && (participant.isBaselineComplete || participant.staff)) {
                this.router.navigate(['home', 'dashboard']);
            } else if (participant && participant.isSetup) {
                this.router.navigate(['baseline']);
            } else if (participant) {
                this.router.navigate(['onboard'])
            } else {
                this.router.navigate(['welcome']);
            }   
        }
    }

    private setupAuthorization(participant:any) {
        if(participant) {
            return this.authorizationService.setup();
        } else {
            return this.authorizationService.reset();
        }
    }

    private setupNotifications(participant:any): Promise<void> {
        if(participant) {
            return this.notificationService.setup();
        } else {
            return Promise.resolve();
        }
    }
}
