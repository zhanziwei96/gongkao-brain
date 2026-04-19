import client from './client'

export interface LoginData {
  username: string
  password: string
}

export interface RegisterData {
  username: string
  email: string
  password: string
}

export const authApi = {
  login: (data: LoginData) => client.post('/auth/login', data),
  register: (data: RegisterData) => client.post('/auth/register', data),
}
