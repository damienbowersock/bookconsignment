import { Module } from '@nestjs/common';
import { ReportsService } from './reports.service';
import { ReportsRouter } from './reports.router';

@Module({
  providers: [ReportsService, ReportsRouter],
  exports: [ReportsRouter, ReportsService]
})
export class ReportsModule {}
