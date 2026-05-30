import { createContext, useContext, useState, useCallback } from 'react'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('admin_token'))
  const [isAuthenticated, setIsAuthenticated] = useState(
    () => !!localStorage.getItem('admin_token')
  )

  const login = useCallback((newToken) => {
    localStorage.setItem('admin_token', newToken)
    setToken(newToken)
    setIsAuthenticated(true)
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('admin_token')
    setToken(null)
    setIsAuthenticated(false)
  }, [])

  return (
    <AuthContext.Provider value={{ token, isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
