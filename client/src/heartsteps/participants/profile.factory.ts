import { Injectable } from "@angular/core";
import { MessageService } from "@heartsteps/notifications/message.service";
import { WalkingSuggestionTimeService } from "@heartsteps/walking-suggestions/walking-suggestion-time.service";
import { PlacesService } from "@heartsteps/places/places.service";
import { ContactInformationService } from "@heartsteps/contact-information/contact-information.service";
import { ReflectionTimeService } from "@heartsteps/weekly-survey/reflection-time.service";
import { FitbitService } from "@heartsteps/fitbit/fitbit.service";
import { CurrentWeekService } from "@heartsteps/current-week/current-week.service";
import { DailyTimeService } from "@heartsteps/daily-times/daily-times.service";
import { ActivityPlanService } from "@heartsteps/activity-plans/activity-plan.service";
import { ActivityTypeService } from "@heartsteps/activity-types/activity-type.service";
import { FitbitWatchService } from "@heartsteps/fitbit-watch/fitbit-watch.service";
import { CachedActivityLogService } from "@heartsteps/activity-logs/cached-activity-log.service";
import { ParticipantInformationService } from "./participant-information.service";


@Injectable()
export class ProfileService {

    constructor(
        private messageService: MessageService,
        private dailyTimeService: DailyTimeService,
        private walkingSuggestionTimeService:WalkingSuggestionTimeService,
        private placesService:PlacesService,
        private contactInformationService: ContactInformationService,
        private reflectionTimeService: ReflectionTimeService,
        private fitbitService: FitbitService,
        private fitbitWatchService: FitbitWatchService,
        private currentWeekService: CurrentWeekService,
        private cachedActivityLogService: CachedActivityLogService,
        private activityPlanService: ActivityPlanService,
        private activityTypeService: ActivityTypeService,
        private participantInformationService: ParticipantInformationService
    ) {}

    public isComplete():Promise<boolean> {
        return this.get()
        .then((profile) => {
            let complete = true
            Object.keys(profile).forEach((key) => {
                if(!profile[key]) {
                    complete = false
                }
            })
            if(complete) {
                return Promise.resolve(true)
            } else {
                return Promise.reject(false)
            }
        })
        .catch(() => {
            return Promise.reject(false)
        })
    }

    public update():Promise<void> {
        return Promise.all([
            this.fitbitService.setup(),
            this.loadCurrentWeek(),
            this.setupActivityLogCache(),
            this.setupActivityPlanService(),
            this.setupActivityTypeService(),
            this.setupDailyTimes(),
        ])
        .then(() => {
            return undefined;
        })
        .catch(() => {
            return Promise.reject("Profile factory did not update participant");
        });
    }

    public load():Promise<boolean> {
        return Promise.all([
            this.loadActivityLogCache(),
            this.loadWalkingSuggestionTimes(),
            this.loadPlaces(),
            this.loadReflectionTime(),
            this.loadContactInformation(),
            this.loadFitbit(),
            this.loadFitbitWatchStatus(),
            this.loadParticipantInformation()
        ])
        .then(() => {
            return this.update();
        })
        .then(() => {
            return Promise.resolve(true);
        })
        .catch(() => {
            return Promise.reject("Complete participant did not load");
        });
    }

    public remove():Promise<boolean> {
        return Promise.all([
            this.walkingSuggestionTimeService.removeTimes(),
            this.placesService.remove(),
            this.reflectionTimeService.remove(),
            this.contactInformationService.remove(),
            this.fitbitService.remove()
        ])
        .then(() => {
            return Promise.resolve(true);
        })
        .catch(() => {
            return Promise.reject("Error removing participant");
        });
    }

    public get():Promise<any> {
        return Promise.all([
            this.checkNotificationsEnabled(),
            this.checkWalkingSuggestions(),
            this.checkPlacesSet(),
            this.checkReflectionTime(),
            this.checkContactInformation(),
            this.checkFitbit(),
            this.checkFitbitWatch()
        ])
        .then((results) => {
            return {
                notificationsEnabled: results[0],
                walkingSuggestionTimes: results[1],
                places: results[2],
                weeklyReflectionTime: results[3],
                contactInformation: results[4],
                fitbitAuthorization: results[5],
                fitbitWatch: results[6]
            }
        })
        .catch(() => {
            return Promise.reject(false)
        })
    }

    private setupDailyTimes():Promise<boolean> {
        return this.dailyTimeService.setup()
        .catch(() => {
            return Promise.resolve(false);
        });
    }

    private checkReflectionTime():Promise<boolean> {
        return this.reflectionTimeService.getTime()
        .then(() => {
            return true
        })
        .catch(() => {
            return Promise.resolve(false)
        })
    }

    private loadReflectionTime():Promise<boolean> {
        return this.reflectionTimeService.load()
        .then(() => {
            return true;
        })
        .catch(() => {
            return Promise.resolve(false);
        });
    }

    private checkContactInformation():Promise<boolean> {
        return this.contactInformationService.get()
        .then(() => {
            return true
        })
        .catch(() => {
            return Promise.resolve(false)
        })
    }

    private loadContactInformation():Promise<boolean> {
        return this.contactInformationService.load()
        .then(() => {
            return true;
        })
        .catch(() => {
            return Promise.resolve(false);
        });
    }

    private checkNotificationsEnabled():Promise<boolean> {
        return this.messageService.requestedPermission()
        .then(() => {
            return true
        })
        .catch(() => {
            return Promise.resolve(false)
        })
    }

    private checkWalkingSuggestions():Promise<boolean> {
        return this.walkingSuggestionTimeService.getTimes()
        .then(() => {
            return true
        })
        .catch(() => {
            return Promise.resolve(false)
        })
    }

    private loadWalkingSuggestionTimes():Promise<boolean> {
        return this.walkingSuggestionTimeService.getTimes()
        .catch(() => {
            return this.walkingSuggestionTimeService.loadTimes()
        })
        .then(() => {
            return true;
        })
        .catch(() => {
            return false
        });
    }

    private checkPlacesSet():Promise<boolean> {
        return this.placesService.getLocations()
        .then(() => {
            return true
        })
        .catch(() => {
            return Promise.resolve(false)
        })
    }

    private loadPlaces():Promise<boolean> {
        return this.placesService.load()
        .then(() => {
            return true;
        })
        .catch(() => {
            return Promise.resolve(false);
        })
    }

    private checkFitbit():Promise<boolean> {
        return this.fitbitService.isAuthorized()
        .then(() => {
            return true;
        })
        .catch(() => {
            return Promise.resolve(false);
        });
    }

    private checkFitbitWatch(): Promise<boolean> {
        return this.fitbitWatchService.isInstalled()
        .then(() => {
            return true;
        })
        .catch(() => {
            return Promise.resolve(false);
        });
    }

    private loadFitbit():Promise<boolean> {
        return this.fitbitService.updateAuthorization()
        .then(() => {
            return true;
        })
        .catch(() => {
            return Promise.resolve(false);
        });
    }

    private loadCurrentWeek():Promise<boolean> {
        return this.currentWeekService.setup()
        .then(() => {
            return true;
        })
        .catch(() => {
            return Promise.resolve(false);
        })
    }

    private setupActivityLogCache(): Promise<boolean> {
        return this.cachedActivityLogService.reload()
        .then(() => {
            return true;
        })
        .catch(() => {
            return Promise.resolve(false);
        })
    }

    private loadActivityLogCache(): Promise<boolean> {
        return this.cachedActivityLogService.update()
        .then(() => {
            return true;
        })
        .catch(() => {
            return false;
        })
    }

    private setupActivityPlanService() {
        return this.activityPlanService.setup()
        .then(() => {
            return true;
        })
        .catch(() => {
            return Promise.resolve(false);
        })
    }

    private setupActivityTypeService() :Promise<boolean> {
        return this.activityTypeService.setup()
        .then(() => {
            return true;
        })
        .catch(() => {
            return Promise.resolve(false);
        })
    }

    private loadParticipantInformation() {
        return this.participantInformationService.load()
        .then(() => {
            return true
        })
        .catch(() => {
            return Promise.resolve(false);
        })
    }

    private loadFitbitWatchStatus(): Promise<boolean> {
        return this.fitbitWatchService.updateStatus()
        .then(() => {
            return true
        })
        .catch(() => {
            return Promise.resolve(false);
        });
    }
}