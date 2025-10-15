import { Injectable, Logger, OnModuleDestroy, OnModuleInit } from '@nestjs/common';
import { PrismaClient } from '@prisma/client';

@Injectable()
export class PrismaService extends PrismaClient implements OnModuleInit, OnModuleDestroy {
  private readonly logger = new Logger(PrismaService.name);

  constructor() {
    super({
      log: [
        { emit: 'event', level: 'query' },
        { emit: 'stdout', level: 'info' },
        { emit: 'stdout', level: 'warn' },
        { emit: 'stdout', level: 'error' }
      ]
    });
  }

  async onModuleInit(): Promise<void> {
    await this.$connect();

    this.$on('query', (event) => {
      this.logger.debug(`Query: ${event.query} Params: ${event.params}`);
    });
  }

  async onModuleDestroy(): Promise<void> {
    await this.$disconnect();
  }

  /**
   * Ensures Prisma is gracefully shutdown when the app closes.
   */
  async enableShutdownHooks(app: { close: () => Promise<void> }): Promise<void> {
    this.$on('beforeExit', async () => {
      await app.close();
    });
  }
}
