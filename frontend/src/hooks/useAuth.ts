import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { authApi } from '@/lib/api'
import type { AuthUser } from '@/types'

export function useAuth() {
  const qc = useQueryClient()

  const { data: user, isLoading } = useQuery<AuthUser>({
    queryKey: ['auth', 'me'],
    queryFn: async () => {
      // If no token stored, skip the network call
      const token = localStorage.getItem('auth_token')
      if (!token) return { authenticated: false } as AuthUser
      const { data } = await authApi.me()
      return data
    },
    retry: false,
    staleTime: 1000 * 60 * 5,
  })

  const loginMutation = useMutation({
    mutationFn: async ({ username, password }: { username: string; password: string }) => {
      const { data } = await authApi.login(username, password)
      // Store the token returned by the backend
      if (data.token) {
        localStorage.setItem('auth_token', data.token)
      }
      return data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['auth', 'me'] })
    },
  })

  const logoutMutation = useMutation({
    mutationFn: async () => {
      try {
        await authApi.logout()
      } finally {
        localStorage.removeItem('auth_token')
      }
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['auth', 'me'] })
      qc.clear()
    },
  })

  return {
    user,
    isLoading,
    isAuthenticated: user?.authenticated ?? false,
    isStaff: user?.isStaff ?? false,
    login: loginMutation.mutateAsync,
    logout: logoutMutation.mutateAsync,
    loginLoading: loginMutation.isPending,
    loginError: loginMutation.error,
  }
}
