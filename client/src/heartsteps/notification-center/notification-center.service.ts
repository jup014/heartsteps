import { Injectable } from "@angular/core";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
// import { Message } from "@heartsteps/notifications/message.model";
// import { MessageService } from "@heartsteps/notifications/message.service";

@Injectable()
export class NotificationCenterService {
    constructor(
        private heartstepsServer: HeartstepsServer // private messageService: MessageService
    ) {}

    public getRecentNotifications(
        cohortId: number,
        userId: string
    ): Promise<any> {
        return this.heartstepsServer.get(
            `/notification_center/${cohortId}/${userId}/`,
            {}
        );
    }

    // public getRecentNotifications(): Promise<any> {
    //     // TODO: remove hardcoded url and use params in get() method
    //     return this.heartstepsServer
    //         .get("1/test/notifications_api", {})
    //         .then((notifications) => {
    //             // TODO: use MessageService to display messages
    //             // TODO: look at activity-survey.service.ts for reference
    //             console.log(notifications);
    //         });
    // }
}
