import { Injectable } from '@nestjs/common';
import { initTRPC } from '@trpc/server';
import superjson from 'superjson';
import { ZodError } from 'zod';
import type { AppContext } from './types';

@Injectable()
export class TrpcService {
  readonly t = initTRPC.context<AppContext>().create({
    transformer: superjson,
    errorFormatter({ shape, error }) {
      return {
        ...shape,
        data: {
          ...shape.data,
          zodError: error.cause instanceof ZodError ? error.cause.flatten() : null
        }
      };
    }
  });

  get router() {
    return this.t.router;
  }

  get procedure() {
    return this.t.procedure;
  }

  get middleware() {
    return this.t.middleware;
  }
}
