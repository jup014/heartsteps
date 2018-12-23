import { Component } from '@angular/core';
import { Platform, ModalController } from 'ionic-angular';
import { StatusBar } from '@ionic-native/status-bar';
import { SplashScreen } from '@ionic-native/splash-screen';
import { ParticipantService } from '@heartsteps/participants/participant.service';
import { BackgroundService } from '@app/background.service';
import { NotificationService } from './notification.service';
import { HeartstepsServer } from '@infrastructure/heartsteps-server.service';
import { EnrollmentModal } from '@heartsteps/enrollment/enroll';
import { AuthorizationService } from './authorization.service';

@Component({
    templateUrl: 'app.html'
})
export class MyApp {
    constructor(
        platform: Platform,
        statusBar: StatusBar,
        splashScreen: SplashScreen,
        private participant:ParticipantService,
        private backgroundService: BackgroundService,
        private notificationService: NotificationService,
        private authorizationService: AuthorizationService
    ) {
        platform.ready()
        .then(() => {
            this.participant.onChange().subscribe((participant: any) => {
                this.setupBackgroundProcess(participant);
                this.setupNotifications(participant);
                this.setupAuthorization(participant);
            });
            return this.participant.update();
        })
        .then(() => {
            statusBar.styleDefault();
            splashScreen.hide();
        });
    }

    setupNotifications(participant:any) {
        if(participant.profileComplete) {
            this.notificationService.setup();
        }
    }

    setupBackgroundProcess(participant:any) {
        if(participant.profileComplete) {
            this.backgroundService.init();
        }
    }

    setupAuthorization(participant:any) {
        if(participant) {
            this.authorizationService.setup()
        } else {
            this.authorizationService.reset();
        }
    }
}

