// URL base del backend — en producción usa VITE_API_URL, en dev usa proxy vacío
let _base = import.meta.env.VITE_API_URL || ''
// Asegurar protocolo absoluto si se ingresó sin https://
if (_base && !_base.startsWith('http')) {
  _base = 'https://' + _base
}
export const API_BASE = _base
