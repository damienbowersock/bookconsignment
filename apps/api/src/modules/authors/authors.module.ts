import { Module } from '@nestjs/common';
import { AuthorsService } from './authors.service';
import { AuthorsRouter } from './authors.router';

@Module({
  providers: [AuthorsService, AuthorsRouter],
  exports: [AuthorsRouter, AuthorsService]
})
export class AuthorsModule {}
