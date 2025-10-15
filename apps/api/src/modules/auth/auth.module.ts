import { Module } from '@nestjs/common';
import { AuthService } from './auth.service';
import { AuthRouter } from './auth.router';
import { TenancyModule } from '../tenancy/tenancy.module';

@Module({
  imports: [TenancyModule],
  providers: [AuthService, AuthRouter],
  exports: [AuthService, AuthRouter]
})
export class AuthModule {}
