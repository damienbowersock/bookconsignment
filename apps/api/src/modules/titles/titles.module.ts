import { Module } from '@nestjs/common';
import { TitlesService } from './titles.service';
import { TitlesRouter } from './titles.router';

@Module({
  providers: [TitlesService, TitlesRouter],
  exports: [TitlesService, TitlesRouter]
})
export class TitlesModule {}
