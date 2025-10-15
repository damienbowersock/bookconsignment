import { Module } from '@nestjs/common';
import { NotificationsService } from './notifications.service';
import { NotificationsRouter } from './notifications.router';

@Module({
  providers: [NotificationsService, NotificationsRouter],
  exports: [NotificationsService, NotificationsRouter]
})
export class NotificationsModule {}
