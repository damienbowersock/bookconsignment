import { Injectable } from '@nestjs/common';

@Injectable()
export class NotificationsService {
  async queueEmail(payload: { to: string; template: string; data: Record<string, unknown> }) {
    // TODO: integrate with Resend/SendGrid.
    return {
      status: 'QUEUED',
      ...payload
    };
  }
}
