import { Module } from '@nestjs/common';
import { TrpcService } from './trpc.service';
import { TrpcRouter } from './trpc.router';
import { AuthorsModule } from '../modules/authors/authors.module';
import { InventoryModule } from '../modules/inventory/inventory.module';
import { SalesModule } from '../modules/sales/sales.module';
import { SettlementsModule } from '../modules/settlements/settlements.module';
import { ReportsModule } from '../modules/reports/reports.module';
import { NotificationsModule } from '../modules/notifications/notifications.module';
import { TitlesModule } from '../modules/titles/titles.module';
import { AuthModule } from '../modules/auth/auth.module';
import { TenancyModule } from '../modules/tenancy/tenancy.module';

@Module({
  imports: [
    AuthModule,
    TenancyModule,
    AuthorsModule,
    TitlesModule,
    InventoryModule,
    SalesModule,
    SettlementsModule,
    ReportsModule,
    NotificationsModule
  ],
  providers: [TrpcService, TrpcRouter],
  exports: [TrpcService, TrpcRouter]
})
export class TrpcModule {}
