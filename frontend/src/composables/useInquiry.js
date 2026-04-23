import { ref, reactive } from 'vue'
import { API_BASE } from './useApi'

const CURRENT_YEAR = new Date().getFullYear()

export function useInquiry(initialBrand = '') {
  const loading = ref(false)
  const success = ref(false)
  const error = ref(null)

  const form = reactive({
    name: '',
    rut: '',
    phone: '',
    email: '',
    brand: initialBrand,
    model: '',
    year: '',
    vin: '',
    description: '',
    product_id: null,
  })

  const errors = reactive({
    name: '',
    rut: '',
    phone: '',
    brand: '',
    model: '',
    year: '',
    vin: '',
    description: '',
  })

  const formatRut = (value) => {
    const clean = value.replace(/[^0-9kK]/g, '').toUpperCase()
    if (clean.length <= 1) return clean
    const body = clean.slice(0, -1)
    const dv = clean.slice(-1)
    const formatted = body.replace(/\B(?=(\d{3})+(?!\d))/g, '.')
    return `${formatted}-${dv}`
  }

  const validateRut = (rut) => {
    const clean = rut.replace(/[^0-9kK]/g, '').toUpperCase()
    if (clean.length < 2) return false
    const body = clean.slice(0, -1)
    const dv = clean.slice(-1)
    let sum = 0
    let multiplier = 2
    for (let i = body.length - 1; i >= 0; i--) {
      sum += parseInt(body[i]) * multiplier
      multiplier = multiplier === 7 ? 2 : multiplier + 1
    }
    const expected = 11 - (sum % 11)
    const expectedDv = expected === 11 ? '0' : expected === 10 ? 'K' : String(expected)
    return dv === expectedDv
  }

  const onRutInput = (e) => {
    form.rut = formatRut(e.target.value)
  }

  const validate = () => {
    let valid = true
    Object.keys(errors).forEach(k => (errors[k] = ''))

    if (!form.name.trim() || form.name.trim().length < 3) {
      errors.name = 'Ingresa tu nombre completo (mínimo 3 caracteres).'
      valid = false
    }
    if (!form.rut) {
      errors.rut = 'El RUT es requerido.'
      valid = false
    } else if (!validateRut(form.rut)) {
      errors.rut = 'El RUT ingresado no es válido.'
      valid = false
    }
    if (!form.phone.trim()) {
      errors.phone = 'El teléfono es requerido.'
      valid = false
    } else if (!/^\+?[\d\s\-()]{7,15}$/.test(form.phone.trim())) {
      errors.phone = 'Ingresa un número de teléfono válido.'
      valid = false
    }
    if (!form.brand) {
      errors.brand = 'Selecciona la marca del vehículo.'
      valid = false
    }
    if (!form.model.trim()) {
      errors.model = 'Ingresa el modelo del vehículo.'
      valid = false
    }
    if (!form.year) {
      errors.year = 'Selecciona el año del vehículo.'
      valid = false
    }
    if (form.vin.trim() && form.vin.replace(/\s/g, '').length !== 17) {
      errors.vin = 'El VIN debe tener exactamente 17 caracteres (o déjalo vacío).'
      valid = false
    }
    if (!form.description.trim() || form.description.trim().length < 10) {
      errors.description = 'Describe el repuesto que necesitas (mínimo 10 caracteres).'
      valid = false
    }

    return valid
  }

  const submitInquiry = async () => {
    if (!validate()) return

    loading.value = true
    error.value = null

    try {
      const payload = {
        name: form.name.trim(),
        rut: form.rut,
        phone: form.phone.trim(),
        brand: form.brand,
        model: form.model.trim(),
        year: parseInt(form.year),
        vin: form.vin.trim().toUpperCase() || null,
        part_description: form.description.trim(),
        product_id: form.product_id || null,
      }

      const res = await fetch(`${API_BASE}/api/inquiries/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        let msg = `Error ${res.status}`
        if (Array.isArray(data?.detail)) {
          msg = data.detail.map(e => e.msg).join(', ')
        } else if (typeof data?.detail === 'string') {
          msg = data.detail
        }
        throw new Error(msg)
      }

      success.value = true
    } catch (e) {
      error.value = e.message || 'Ocurrió un error al enviar tu solicitud. Por favor intenta de nuevo.'
    } finally {
      loading.value = false
    }
  }

  const years = Array.from({ length: CURRENT_YEAR - 1989 }, (_, i) => CURRENT_YEAR - i)

  return {
    form,
    errors,
    loading,
    success,
    error,
    onRutInput,
    submitInquiry,
    years,
  }
}
