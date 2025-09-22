import { z } from 'zod'

export const signUpSchema = z.object({
  full_name: z
    .string()
    .min(2, 'Name must be at least 2 characters')
    .max(50, 'Name must be less than 50 characters')
    .regex(/^[a-zA-Z\s]+$/, 'Name can only contain letters and spaces'),
  
  email: z
    .string()
    .email('Please enter a valid email address')
    .min(1, 'Email is required'),
  
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters')
    .regex(
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/,
      'Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character'
    ),
  
  privacy_policy: z
    .boolean()
    .refine(val => val === true, 'You must accept the Privacy Policy'),
  
  terms_of_service: z
    .boolean()
    .refine(val => val === true, 'You must accept the Terms of Service'),
  
  age_confirmation: z
    .boolean()
    .refine(val => val === true, 'You must confirm you are 18 years or older')
})

export const signInSchema = z.object({
  email: z
    .string()
    .email('Please enter a valid email address')
    .min(1, 'Email is required'),
  
  password: z
    .string()
    .min(1, 'Password is required'),
  
  remember_me: z.boolean().optional()
})

export const forgotPasswordSchema = z.object({
  email: z
    .string()
    .email('Please enter a valid email address')
    .min(1, 'Email is required')
})

export type SignUpFormData = z.infer<typeof signUpSchema>
export type SignInFormData = z.infer<typeof signInSchema>
export type ForgotPasswordFormData = z.infer<typeof forgotPasswordSchema>
