import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams } from 'ionic-angular';
import { EnrollmentService } from '../../heartsteps/enrollment.service';
import { HomePage } from '../home/home';

/**
 * Generated class for the EnrollPage page.
 *
 * See https://ionicframework.com/docs/components/#navigation for more info on
 * Ionic pages and navigation.
 */

@IonicPage()
@Component({
  selector: 'page-enroll',
  templateUrl: 'enroll.html',
  providers: [ EnrollmentService ]
})
export class EnrollPage {

  // Enrollment token enterd by user
  enrollmentToken:String;
  error:Boolean;

  constructor(private enrollmentService: EnrollmentService, public navCtrl: NavController, public navParams: NavParams) {}

  enroll() {
    if(!this.enrollmentToken || this.enrollmentToken==="") {
      return;
    }

    let service = this;
    service.error = false;
    
    this.enrollmentService.enroll(this.enrollmentToken)
    .then(function() {
      service.navCtrl.setRoot(HomePage);
      service.navCtrl.popToRoot();
    })
    .catch(function(){
      service.error = true;
    })

    
  }

  ionViewDidLoad() {
    console.log('ionViewDidLoad EnrollPage');
  }

}
