import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { PrismaModule } from './prisma/prisma.module';
import { TrpcModule } from './trpc/trpc.module';
import { AuthModule } from './modules/auth/auth.module';
import { TenancyModule } from './modules/tenancy/tenancy.module';
import { AuthorsModule } from './modules/authors/authors.module';
import { TitlesModule } from './modules/titles/titles.module';
import { InventoryModule } from './modules/inventory/inventory.module';
import { SalesModule } from './modules/sales/sales.module';
import { SettlementsModule } from './modules/settlements/settlements.module';
import { ReportsModule } from './modules/reports/reports.module';
import { NotificationsModule } from './modules/notifications/notifications.module';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
      envFilePath: ['.env', '../../.env'],
      cache: true
    }),
    PrismaModule,
    TenancyModule,
    AuthModule,
    AuthorsModule,
    TitlesModule,
    InventoryModule,
    SalesModule,
    SettlementsModule,
    ReportsModule,
    NotificationsModule,
    TrpcModule
  ]
})
export class AppModule {}
