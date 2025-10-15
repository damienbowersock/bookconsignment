import { Injectable } from '@nestjs/common';
import type { INestApplication } from '@nestjs/common';
import { createExpressMiddleware } from '@trpc/server/adapters/express';
import { randomUUID } from 'node:crypto';
import { TrpcService } from './trpc.service';
import type { AppContext } from './types';
import { AuthService } from '../modules/auth/auth.service';
import { AuthRouter } from '../modules/auth/auth.router';
import { AuthorsRouter } from '../modules/authors/authors.router';
import { TitlesRouter } from '../modules/titles/titles.router';
import { InventoryRouter } from '../modules/inventory/inventory.router';
import { SalesRouter } from '../modules/sales/sales.router';
import { SettlementsRouter } from '../modules/settlements/settlements.router';
import { ReportsRouter } from '../modules/reports/reports.router';
import { NotificationsRouter } from '../modules/notifications/notifications.router';

@Injectable()
export class TrpcRouter {
  private readonly appRouter;

  constructor(
    private readonly trpc: TrpcService,
    private readonly authService: AuthService,
    private readonly authRouter: AuthRouter,
    private readonly authorsRouter: AuthorsRouter,
    private readonly titlesRouter: TitlesRouter,
    private readonly inventoryRouter: InventoryRouter,
    private readonly salesRouter: SalesRouter,
    private readonly settlementsRouter: SettlementsRouter,
    private readonly reportsRouter: ReportsRouter,
    private readonly notificationsRouter: NotificationsRouter
  ) {
    this.appRouter = this.trpc.router({
      health: this.trpc.procedure.query(() => ({ status: 'ok' })),
      auth: this.authRouter.createRouter(),
      authors: this.authorsRouter.createRouter(),
      titles: this.titlesRouter.createRouter(),
      inventory: this.inventoryRouter.createRouter(),
      sales: this.salesRouter.createRouter(),
      settlements: this.settlementsRouter.createRouter(),
      reports: this.reportsRouter.createRouter(),
      notifications: this.notificationsRouter.createRouter()
    });
  }

  getRouter() {
    return this.appRouter;
  }

  applyMiddleware(app: INestApplication) {
    const createContext = async ({ req, res }): Promise<AppContext> => {
      const requestId = (req.headers['x-request-id'] as string | undefined) ?? randomUUID();
      const { user, tenantId } = await this.authService.authenticateRequest(req);
      return {
        req,
        res,
        user,
        tenantId,
        requestId
      };
    };

    const middleware = createExpressMiddleware({
      router: this.appRouter,
      createContext
    });

    const httpAdapter = app.getHttpAdapter();
    httpAdapter.getInstance().use('/trpc', middleware);
  }
}

export type AppRouter = ReturnType<TrpcRouter['getRouter']>;
