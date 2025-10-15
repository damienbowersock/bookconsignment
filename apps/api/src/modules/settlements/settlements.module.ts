import { Module } from '@nestjs/common';
import { SettlementsService } from './settlements.service';
import { SettlementsRouter } from './settlements.router';

@Module({
  providers: [SettlementsService, SettlementsRouter],
  exports: [SettlementsService, SettlementsRouter]
})
export class SettlementsModule {}
