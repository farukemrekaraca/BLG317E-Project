export interface TransactionBase {
  price: number
  payment_method: string
  installment_period?: number
}

export interface TransactionCreate extends TransactionBase {
  ticket_ids: number[]
}

export interface TransactionResponse extends TransactionBase {
  transaction_id: number
  user_id: number
  date: string
  receipt_id: string
}

export interface TransactionItem {
  transaction_item_id: number
  transaction_id: number
  ticket_id: number
}

export enum PaymentMethod {
  CREDIT_CARD = 'Credit Card',
  DEBIT_CARD = 'Debit Card',
  BANK_TRANSFER = 'Bank Transfer',
  CASH = 'Cash'
}
