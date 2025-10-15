import { Module } from '@nestjs/common';
import { SalesService } from './sales.service';
import { SalesRouter } from './sales.router';

@Module({
  providers: [SalesService, SalesRouter],
  exports: [SalesService, SalesRouter]
})
export class SalesModule {}
