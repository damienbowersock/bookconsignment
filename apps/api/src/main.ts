import { Logger, ValidationPipe } from '@nestjs/common';
import { NestFactory } from '@nestjs/core';
import { ConfigService } from '@nestjs/config';
import helmet from 'helmet';
import { parse as parseCookies } from 'cookie';
import cors from 'cors';
import { AppModule } from './app.module';
import { PrismaService } from './prisma/prisma.service';
import { TrpcRouter } from './trpc/trpc.router';

async function bootstrap(): Promise<void> {
  const app = await NestFactory.create(AppModule, {
    bufferLogs: true
  });
  const logger = new Logger('Bootstrap');
  const config = app.get(ConfigService);

  app.use(
    helmet({
      crossOriginResourcePolicy: { policy: 'cross-origin' }
    })
  );

  app.use(cors({ origin: config.get<string>('WEB_ORIGIN') ?? '*', credentials: true }));

  app.use((req, _res, next) => {
    req['cookies'] = parseCookies(req.headers.cookie ?? '');
    next();
  });

  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      transform: true,
      forbidUnknownValues: true
    })
  );

  const prisma = app.get(PrismaService);
  await prisma.enableShutdownHooks(app as unknown as { close: () => Promise<void> });

  const trpcRouter = app.get(TrpcRouter);
  trpcRouter.applyMiddleware(app);

  const port = config.get<number>('PORT') ?? 4000;

  await app.listen(port);
  logger.log(`API listening on port ${port}`);
}

void bootstrap();
