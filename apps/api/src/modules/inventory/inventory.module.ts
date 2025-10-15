import { Module } from '@nestjs/common';
import { InventoryService } from './inventory.service';
import { InventoryRouter } from './inventory.router';

@Module({
  providers: [InventoryService, InventoryRouter],
  exports: [InventoryService, InventoryRouter]
})
export class InventoryModule {}
