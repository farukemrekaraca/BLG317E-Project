export interface UserType {
  user_type_id: number
  type_name: string
  authorization_level: number
}

export interface UserBase {
  name: string
  mail_address: string
  phone_number?: string
}

export interface UserCreate extends UserBase {
  password: string
  type_id: number
}

export interface UserLogin {
  mail_address: string
  password: string
}

export interface UserResponse extends UserBase {
  user_id: number
  type_id: number
  created_at: string
}

export interface Token {
  access_token: string
  token_type: string
}

export interface TokenData {
  user_id?: number
}

export enum UserRole {
  ADMIN = 1,
  ORGANIZER = 2,
  VENUE_OWNER = 3,
  ATTENDEE = 4
}

export const UserRoleLabels: Record<UserRole, string> = {
  [UserRole.ADMIN]: 'Admin',
  [UserRole.ORGANIZER]: 'Organizer',
  [UserRole.VENUE_OWNER]: 'Venue Owner',
  [UserRole.ATTENDEE]: 'Attendee'
}
