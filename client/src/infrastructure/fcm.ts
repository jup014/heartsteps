import { Injectable } from "@angular/core";
import { Platform } from "ionic-angular";
import { Firebase as FirebaseNative } from '@ionic-native/firebase';
import firebase from 'firebase/app';
import 'firebase/messaging';
import { Observable } from "rxjs/Observable";
import { Subject } from "rxjs/Subject";
import { Storage } from '@ionic/storage';

declare var process: {
    env: {
        FIREBASE_MESSAGING_SENDER_ID: string
    }
}

@Injectable()
export class FcmService {

    private firebaseMessaging:any;
    private firebase: FirebaseNative;

    private messageSubject:Subject<any>;
    private dataSubject:Subject<any>;

    private subscriptionSetup:boolean;

    constructor(
        private platform: Platform,
        private storage:Storage
    ) {
        this.messageSubject = new Subject();
        this.dataSubject = new Subject();

        if(this.platform.is('ios') || this.platform.is('android')) {
            this.setupNative();
        } else {
            this.setupWeb();
        }
        this.setupSubscription()
        .catch(() => {
            console.log("no subscription")
        });
    }

    private directMessage(message:any) {
        if(message.aps && message.aps.alert) {
            this.messageSubject.next(message.aps.alert)
        }
        else if(message.body && message.title) {
            this.messageSubject.next(message);
        } else {
            this.dataSubject.next(message);
        }
    }

    onMessage():Observable<any> {
        return this.messageSubject.asObservable();
    }

    onDataMessage():Observable<any> {
        return this.dataSubject.asObservable();
    }

    getDeviceType():string {
        if(this.platform.is('ios')) {
            return 'ios';
        }
        if(this.platform.is('android')) {
            return 'android';
        }
        return 'web';
    }

    getPermission():Promise<boolean> {
        if(this.platform.is('ios')) {
            return this.firebase.grantPermission()
        }

        if(this.platform.is('android')) {
            return Promise.resolve(true);
        }

        return this.firebaseMessaging.requestPermission();
    }

    getToken():Promise<string> {
        return this.getTokenWrapper()
        .then((token) => {
            return this.saveToken(token)
        })
        .then((token) => {
            if(!this.subscriptionSetup) {
                this.setupSubscription();
            }
            return token
        });
    }

    saveToken(token:string):Promise<string> {
        return new Promise((resolve, reject) => {
            return this.storage.set('fcmToken', token)
            .then(() => {
                resolve(token)
            })
            .catch(() => {
                reject()
            })
        })
    }

    private getTokenWrapper():Promise<string> {
        if(this.platform.is('ios') || this.platform.is('android')) {
            return this.firebase.getToken();
        } else {
            return this.firebaseMessaging.getToken();
        }
    }

    private setupSubscription():Promise<boolean> {
        console.log("try to setup supscription....")
        return this.storage.get('fcmToken')
        .then((token) => {
            if(!token) {
                return Promise.reject(false)
            }

            if(this.platform.is('ios') || this.platform.is('android')) {
                console.log("Setting up subscription")
                this.firebase.onNotificationOpen().subscribe((data) => {
                    this.directMessage(data);
                    console.log("got message")
                });
            } else {
               this.firebaseMessaging.onMessage((data:any) => {
                    if(data.notification){
                        // should merge notification object into data object
                        // to match cordova implementation
                        this.directMessage(data.notification);
                    } else {
                        this.directMessage(data);
                    }
                });
            }
            this.subscriptionSetup = true
            return Promise.resolve(true)
        })
        .catch(() => {
            this.subscriptionSetup = false
            return Promise.reject(false)
        })
    }

    private setupWeb() {
        firebase.initializeApp({
            messagingSenderId: process.env.FIREBASE_MESSAGING_SENDER_ID
        });
        this.firebaseMessaging = firebase.messaging();
    }

    private setupNative() {
        this.firebase = new FirebaseNative();
    }
}