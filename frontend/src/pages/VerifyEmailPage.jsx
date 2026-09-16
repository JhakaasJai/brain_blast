import React, { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { verifyEmail } from '../services/api'
import { useAuth } from '../components/AuthContext'

export default function VerifyEmailPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const { signIn } = useAuth()
  const [status, setStatus] = useState('Verifying your email...')

  useEffect(() => {
    const token = searchParams.get('token')
    if (!token) {
      setStatus('No verification token provided in the URL.')
      return
    }
    
    verifyEmail(token)
      .then(data => {
        signIn({ id: data.user_id, role: data.role, email: "User" }, data.access_token, data.refresh_token)
        setStatus('Email verified successfully! Redirecting...')
        setTimeout(() => {
          navigate(data.role === 'patient' ? '/onboarding' : '/dashboard')
        }, 1500)
      })
      .catch(err => {
        setStatus('Verification failed: ' + (err.response?.data?.detail || err.message))
      })
  }, [searchParams, navigate, signIn])

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--color-bg)' }}>
      <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
        <h2>{status}</h2>
      </div>
    </div>
  )
}
