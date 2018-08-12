import { NgModule } from '@angular/core';
import { IonicStorageModule } from '@ionic/storage';
import { FcmService } from './fcm';
import { HeartstepsServer } from './heartsteps-server.service';
import { AuthorizationService } from './authorization.service';
import { loadingService } from './loading.service';
import { Geolocation } from '@ionic-native/geolocation';

@NgModule({
  declarations: [],
  imports: [
    IonicStorageModule.forRoot()
  ],
  entryComponents: [],
  providers: [
      AuthorizationService,
      FcmService,
      HeartstepsServer,
      loadingService,
      Geolocation
  ]
})
export class InfrastructureModule {}
