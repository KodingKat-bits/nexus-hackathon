# NexusMart Business Rules

## Inventory Status

- OUT_OF_STOCK: Product currently has no stock. Recommended action: replenish immediately.
- LOW_STOCK: Product stock is at or below its reorder level. Recommended action: prioritize replenishment.
- OVERSTOCK: Product stock is at least 5 times its reorder level. Recommended action: review excess inventory before ordering more.
- NORMAL: Product inventory is neither low nor overstocked. No immediate inventory action is required.

## Stockout Risk

- HIGH: Estimated stockout within 3 days. Recommended action: prioritize replenishment urgently.
- MEDIUM: Estimated stockout within 5 days. Recommended action: plan replenishment soon.

## Assumptions

- Inventory status is based on the observed current stock and dataset reorder level.
- Overstock uses the 5x reorder-level threshold defined by this project.
- Stockout risk assumes recent average daily sales continue at approximately the observed rate.
- These rules explain deterministic analytics results; they do not create or calculate business numbers.
