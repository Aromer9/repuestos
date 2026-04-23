<template>
  <div class="min-h-screen bg-slate-50">

    <!-- Sidebar -->
    <aside class="fixed inset-y-0 left-0 w-60 bg-[#003087] flex flex-col z-30">
      <div class="px-5 py-5 border-b border-white/10">
        <div class="flex items-center gap-2">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="white" stroke-width="2" stroke-linecap="round">
            <path d="M3 5 Q12 9 21 5"/>
            <line x1="7" y1="5" x2="7" y2="19"/>
            <line x1="17" y1="5" x2="17" y2="19"/>
            <path d="M3 19 Q12 15 21 19"/>
          </svg>
          <span class="text-white font-bold text-base tracking-tight">ARGParts</span>
        </div>
        <p class="text-white/50 text-xs mt-1">Panel de administración</p>
      </div>

      <nav class="flex-1 px-3 py-4 space-y-1">
        <button @click="activeTab = 'inquiries'"
          class="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition"
          :class="activeTab === 'inquiries' ? 'bg-white/15 text-white' : 'text-white/60 hover:bg-white/10 hover:text-white'">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
          </svg>
          Cotizaciones
          <span v-if="pendingCount > 0" class="ml-auto bg-[#0055A5] text-white text-xs font-bold px-2 py-0.5 rounded-full">{{ pendingCount }}</span>
        </button>

        <button @click="activeTab = 'partners'; fetchPartners()"
          class="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition"
          :class="activeTab === 'partners' ? 'bg-white/15 text-white' : 'text-white/60 hover:bg-white/10 hover:text-white'">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
          </svg>
          Partners
          <span class="ml-auto text-white/30 text-xs">{{ partners.length }}</span>
        </button>

        <button @click="activeTab = 'users'"
          class="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition"
          :class="activeTab === 'users' ? 'bg-white/15 text-white' : 'text-white/60 hover:bg-white/10 hover:text-white'">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/>
          </svg>
          Usuarios
        </button>
      </nav>

      <div class="px-3 py-4 border-t border-white/10">
        <div class="flex items-center gap-2 px-3 py-2 mb-2">
          <div class="w-7 h-7 rounded-full bg-white/20 flex items-center justify-center text-white text-xs font-bold uppercase">
            {{ user?.username?.charAt(0) }}
          </div>
          <div class="min-w-0">
            <p class="text-white text-sm font-medium truncate">{{ user?.full_name || user?.username }}</p>
            <p class="text-white/40 text-xs">{{ user?.role }}</p>
          </div>
        </div>
        <button @click="handleLogout"
          class="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-white/60 hover:text-white hover:bg-white/10 text-sm transition">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
          </svg>
          Cerrar sesión
        </button>
      </div>
    </aside>

    <!-- Main -->
    <main class="ml-60 min-h-screen">

      <!-- ========== COTIZACIONES ========== -->
      <template v-if="activeTab === 'inquiries'">
        <div class="px-8 py-6 border-b border-slate-200 bg-white flex items-center justify-between">
          <div>
            <h1 class="text-xl font-semibold text-slate-900">Cotizaciones</h1>
            <p class="text-slate-500 text-sm mt-0.5">{{ inquiries.length }} solicitudes en total</p>
          </div>
          <div class="flex items-center gap-2">
            <select v-model="statusFilter" @change="fetchInquiries"
              class="px-3 py-2 text-sm border border-slate-200 rounded-lg text-slate-700 bg-white focus:outline-none focus:ring-2 focus:ring-[#0055A5]">
              <option value="">Todos los estados</option>
              <option value="pending">Pendientes</option>
              <option value="quoted">Cotizados</option>
              <option value="closed">Cerrados</option>
            </select>
            <button @click="fetchInquiries" class="p-2 rounded-lg text-slate-500 hover:bg-slate-100 transition">
              <svg class="w-4 h-4" :class="{ 'animate-spin': loadingData }" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
              </svg>
            </button>
          </div>
        </div>

        <div class="px-8 py-5 grid grid-cols-3 gap-4">
          <div class="bg-white rounded-xl border border-slate-200 p-4">
            <p class="text-xs font-medium text-slate-500 uppercase tracking-wide">Pendientes</p>
            <p class="text-2xl font-bold text-amber-600 mt-1">{{ pendingCount }}</p>
          </div>
          <div class="bg-white rounded-xl border border-slate-200 p-4">
            <p class="text-xs font-medium text-slate-500 uppercase tracking-wide">Cotizados</p>
            <p class="text-2xl font-bold text-[#0055A5] mt-1">{{ quotedCount }}</p>
          </div>
          <div class="bg-white rounded-xl border border-slate-200 p-4">
            <p class="text-xs font-medium text-slate-500 uppercase tracking-wide">Cerrados</p>
            <p class="text-2xl font-bold text-slate-400 mt-1">{{ closedCount }}</p>
          </div>
        </div>

        <div v-if="loadingData" class="px-8 py-16 text-center text-slate-400">
          <svg class="w-8 h-8 animate-spin mx-auto mb-3" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
          </svg>
          Cargando cotizaciones...
        </div>

        <div v-else class="px-8 pb-8">
          <div v-if="inquiries.length === 0" class="bg-white rounded-xl border border-slate-200 py-16 text-center text-slate-400">
            No hay cotizaciones con ese filtro.
          </div>
          <div v-else class="bg-white rounded-xl border border-slate-200 overflow-hidden">
            <table class="w-full text-sm">
              <thead>
                <tr class="border-b border-slate-100">
                  <th class="text-left px-5 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Cliente</th>
                  <th class="text-left px-5 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Vehículo</th>
                  <th class="text-left px-5 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Repuesto</th>
                  <th class="text-left px-5 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Estado</th>
                  <th class="text-left px-5 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Agente</th>
                  <th class="text-left px-5 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Fecha</th>
                  <th class="px-5 py-3"></th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100">
                <tr v-for="inq in inquiries" :key="inq.id"
                  class="hover:bg-slate-50 transition cursor-pointer" @click="openDetail(inq)">
                  <td class="px-5 py-3.5">
                    <p class="font-medium text-slate-900">{{ inq.name }}</p>
                    <p class="text-slate-400 text-xs">{{ inq.phone }}</p>
                  </td>
                  <td class="px-5 py-3.5">
                    <p class="text-slate-700">{{ inq.brand }} {{ inq.model }}</p>
                    <p class="text-slate-400 text-xs">{{ inq.year }}</p>
                  </td>
                  <td class="px-5 py-3.5 max-w-xs">
                    <p class="text-slate-700 truncate">{{ inq.part_description }}</p>
                    <p v-if="inq.vin" class="text-slate-400 text-xs font-mono">{{ inq.vin }}</p>
                  </td>
                  <td class="px-5 py-3.5">
                    <StatusBadge :status="inq.status" />
                  </td>
                  <td class="px-5 py-3.5">
                    <AgentBadge :agent_status="inq.agent_status" />
                  </td>
                  <td class="px-5 py-3.5 text-slate-400 text-xs whitespace-nowrap">{{ formatDate(inq.created_at) }}</td>
                  <td class="px-5 py-3.5" @click.stop>
                    <div class="flex items-center gap-1">
                      <button v-for="s in ['pending','quoted','closed']" :key="s"
                        v-if="inq.status !== s" @click="changeStatus(inq, s)"
                        class="px-2 py-1 rounded text-xs font-medium border transition"
                        :class="statusBtnClass(s)">{{ statusLabel(s) }}</button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </template>

      <!-- ========== PARTNERS ========== -->
      <template v-if="activeTab === 'partners'">
        <div class="px-8 py-6 border-b border-slate-200 bg-white flex items-center justify-between">
          <div>
            <h1 class="text-xl font-semibold text-slate-900">Partners / Proveedores</h1>
            <p class="text-slate-500 text-sm mt-0.5">El agente OpenClaw cotizará con todos estos proveedores en paralelo</p>
          </div>
          <button @click="openPartnerModal()"
            class="flex items-center gap-2 px-4 py-2 rounded-lg text-white text-sm font-medium"
            style="background-color: #003087;">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path d="M12 4v16m8-8H4"/>
            </svg>
            Nuevo partner
          </button>
        </div>

        <div class="px-8 py-6">
          <div v-if="partners.length === 0" class="bg-white rounded-xl border border-slate-200 py-16 text-center">
            <svg class="w-10 h-10 text-slate-300 mx-auto mb-3" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
              <path d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
            </svg>
            <p class="text-slate-400 text-sm">Aún no hay partners registrados.</p>
            <button @click="openPartnerModal()" class="mt-3 text-sm text-[#0055A5] hover:underline">Agregar el primero</button>
          </div>

          <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            <div v-for="p in partners" :key="p.id"
              class="bg-white rounded-xl border border-slate-200 p-5 flex flex-col gap-3 hover:shadow-sm transition">
              <div class="flex items-start justify-between">
                <div>
                  <p class="font-semibold text-slate-900">{{ p.name }}</p>
                  <span class="inline-block mt-1 px-2 py-0.5 rounded-full text-xs font-medium bg-[#003087]/8 text-[#003087]">{{ p.brand }}</span>
                </div>
                <div class="flex gap-1">
                  <button @click="openPartnerModal(p)" class="p-1.5 rounded-lg text-slate-400 hover:text-[#0055A5] hover:bg-blue-50 transition">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                      <path d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                    </svg>
                  </button>
                  <button @click="deletePartner(p)" class="p-1.5 rounded-lg text-slate-400 hover:text-red-500 hover:bg-red-50 transition">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                      <path d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                    </svg>
                  </button>
                </div>
              </div>
              <div class="space-y-1.5 text-sm text-slate-500">
                <div class="flex items-center gap-2">
                  <svg class="w-3.5 h-3.5 flex-shrink-0 text-slate-400" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
                  </svg>
                  {{ p.phone }}
                </div>
                <div class="flex items-start gap-2">
                  <svg class="w-3.5 h-3.5 flex-shrink-0 mt-0.5 text-slate-400" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path d="M17.657 16.657L13.414 20.9a2 2 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/><path d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
                  </svg>
                  {{ p.address }}
                </div>
                <div v-if="p.notes" class="flex items-start gap-2 text-slate-400 italic">
                  <svg class="w-3.5 h-3.5 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z"/>
                  </svg>
                  {{ p.notes }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- ========== USUARIOS ========== -->
      <template v-if="activeTab === 'users'">
        <div class="px-8 py-6 border-b border-slate-200 bg-white flex items-center justify-between">
          <div>
            <h1 class="text-xl font-semibold text-slate-900">Usuarios admin</h1>
            <p class="text-slate-500 text-sm mt-0.5">Gestiona el acceso al panel</p>
          </div>
          <button @click="showNewUser = true"
            class="flex items-center gap-2 px-4 py-2 rounded-lg text-white text-sm font-medium"
            style="background-color: #003087;">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path d="M12 4v16m8-8H4"/>
            </svg>
            Nuevo usuario
          </button>
        </div>
        <div class="px-8 py-6">
          <div class="bg-white rounded-xl border border-slate-200 overflow-hidden">
            <table class="w-full text-sm">
              <thead>
                <tr class="border-b border-slate-100">
                  <th class="text-left px-5 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Usuario</th>
                  <th class="text-left px-5 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Rol</th>
                  <th class="text-left px-5 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Estado</th>
                  <th class="text-left px-5 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Creado</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100">
                <tr v-for="u in adminUsers" :key="u.id" class="hover:bg-slate-50">
                  <td class="px-5 py-3.5">
                    <p class="font-medium text-slate-900">{{ u.full_name }}</p>
                    <p class="text-slate-400 text-xs">@{{ u.username }}</p>
                  </td>
                  <td class="px-5 py-3.5">
                    <span class="px-2 py-0.5 rounded-full text-xs font-semibold bg-[#003087]/10 text-[#003087]">{{ u.role }}</span>
                  </td>
                  <td class="px-5 py-3.5">
                    <span class="px-2 py-0.5 rounded-full text-xs font-semibold"
                      :class="u.active ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-500'">
                      {{ u.active ? 'Activo' : 'Inactivo' }}
                    </span>
                  </td>
                  <td class="px-5 py-3.5 text-slate-400 text-xs">{{ formatDate(u.created_at) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div v-if="showNewUser" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 px-4">
          <div class="bg-white rounded-2xl shadow-xl w-full max-w-md p-6">
            <h2 class="text-lg font-semibold text-slate-900 mb-4">Nuevo usuario</h2>
            <form @submit.prevent="createUser" class="space-y-3">
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">Nombre completo</label>
                <input v-model="newUser.full_name" type="text" required class="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#0055A5]"/>
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">Usuario</label>
                <input v-model="newUser.username" type="text" required class="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#0055A5]"/>
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">Contraseña</label>
                <input v-model="newUser.password" type="password" required minlength="6" class="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#0055A5]"/>
              </div>
              <div v-if="userError" class="text-red-600 text-sm bg-red-50 rounded-lg px-3 py-2 border border-red-200">{{ userError }}</div>
              <div class="flex gap-2 pt-2">
                <button type="button" @click="showNewUser = false" class="flex-1 py-2 rounded-lg border border-slate-200 text-slate-700 text-sm font-medium hover:bg-slate-50 transition">Cancelar</button>
                <button type="submit" class="flex-1 py-2 rounded-lg text-white text-sm font-medium" style="background-color: #003087;">Crear</button>
              </div>
            </form>
          </div>
        </div>
      </template>

      <!-- Modal detalle cotización -->
      <div v-if="selectedInquiry" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 px-4" @click.self="selectedInquiry = null">
        <div class="bg-white rounded-2xl shadow-xl w-full max-w-lg p-6">
          <div class="flex items-start justify-between mb-4">
            <div>
              <h2 class="text-lg font-semibold text-slate-900">{{ selectedInquiry.name }}</h2>
              <p class="text-slate-500 text-sm">{{ selectedInquiry.rut }} · {{ selectedInquiry.phone }}</p>
            </div>
            <StatusBadge :status="selectedInquiry.status" />
          </div>
          <div class="grid grid-cols-2 gap-3 text-sm mb-4">
            <div class="bg-slate-50 rounded-lg p-3">
              <p class="text-slate-400 text-xs mb-0.5">Vehículo</p>
              <p class="font-medium text-slate-900">{{ selectedInquiry.brand }} {{ selectedInquiry.model }} {{ selectedInquiry.year }}</p>
            </div>
            <div class="bg-slate-50 rounded-lg p-3">
              <p class="text-slate-400 text-xs mb-0.5">VIN</p>
              <p class="font-mono text-slate-900 text-xs">{{ selectedInquiry.vin || '—' }}</p>
            </div>
            <div class="bg-slate-50 rounded-lg p-3 col-span-2">
              <p class="text-slate-400 text-xs mb-0.5">Repuesto solicitado</p>
              <p class="text-slate-900">{{ selectedInquiry.part_description }}</p>
            </div>
          </div>
          <div class="flex flex-wrap gap-2">
            <button v-for="s in ['pending','quoted','closed']" :key="s"
              :disabled="selectedInquiry.status === s"
              @click="changeStatus(selectedInquiry, s); selectedInquiry = null"
              class="px-3 py-1.5 rounded-lg text-xs font-medium border transition"
              :class="selectedInquiry.status === s ? 'opacity-40 cursor-default border-slate-200 text-slate-400' : statusBtnClass(s)">
              {{ statusLabel(s) }}
            </button>
            <button @click="selectedInquiry = null" class="ml-auto px-3 py-1.5 rounded-lg text-xs font-medium border border-slate-200 text-slate-600 hover:bg-slate-50 transition">Cerrar</button>
          </div>
        </div>
      </div>

      <!-- Modal partner (crear / editar) -->
      <div v-if="showPartnerModal" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 px-4">
        <div class="bg-white rounded-2xl shadow-xl w-full max-w-md p-6">
          <h2 class="text-lg font-semibold text-slate-900 mb-4">
            {{ editingPartner ? 'Editar partner' : 'Nuevo partner' }}
          </h2>
          <form @submit.prevent="savePartner" class="space-y-3">
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">Nombre del proveedor <span class="text-red-400">*</span></label>
              <input v-model="partnerForm.name" type="text" required placeholder="Ej: Repuestos Yamamoto"
                class="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#0055A5]"/>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">Marca / especialidad <span class="text-red-400">*</span></label>
              <input v-model="partnerForm.brand" type="text" required placeholder="Ej: Subaru, Toyota, Multimarco"
                class="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#0055A5]"/>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">Dirección <span class="text-red-400">*</span></label>
              <input v-model="partnerForm.address" type="text" required placeholder="Ej: Av. Matta 1234, Santiago"
                class="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#0055A5]"/>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">Teléfono <span class="text-red-400">*</span></label>
              <input v-model="partnerForm.phone" type="tel" required placeholder="Ej: +56912345678"
                class="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#0055A5]"/>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">Notas <span class="text-slate-400 font-normal">(opcional)</span></label>
              <textarea v-model="partnerForm.notes" rows="2" placeholder="Ej: Solo repuestos originales, no alternativos"
                class="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#0055A5] resize-none"/>
            </div>
            <div v-if="partnerError" class="text-red-600 text-sm bg-red-50 rounded-lg px-3 py-2 border border-red-200">{{ partnerError }}</div>
            <div class="flex gap-2 pt-1">
              <button type="button" @click="showPartnerModal = false"
                class="flex-1 py-2 rounded-lg border border-slate-200 text-slate-700 text-sm font-medium hover:bg-slate-50 transition">Cancelar</button>
              <button type="submit"
                class="flex-1 py-2 rounded-lg text-white text-sm font-medium transition"
                style="background-color: #003087;">
                {{ editingPartner ? 'Guardar cambios' : 'Crear partner' }}
              </button>
            </div>
          </form>
        </div>
      </div>

    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const { user, logout, authFetch } = useAuth()

const activeTab = ref('inquiries')

// Cotizaciones
const inquiries = ref([])
const loadingData = ref(false)
const statusFilter = ref('')
const selectedInquiry = ref(null)

// Usuarios
const adminUsers = ref([])
const showNewUser = ref(false)
const userError = ref('')
const newUser = ref({ username: '', password: '', full_name: '', role: 'admin' })

// Partners
const partners = ref([])
const showPartnerModal = ref(false)
const editingPartner = ref(null)
const partnerError = ref('')
const emptyPartnerForm = () => ({ name: '', brand: '', address: '', phone: '', notes: '' })
const partnerForm = ref(emptyPartnerForm())

const pendingCount = computed(() => inquiries.value.filter(i => i.status === 'pending').length)
const quotedCount  = computed(() => inquiries.value.filter(i => i.status === 'quoted').length)
const closedCount  = computed(() => inquiries.value.filter(i => i.status === 'closed').length)

// --- Cotizaciones ---
const fetchInquiries = async () => {
  loadingData.value = true
  try {
    const url = statusFilter.value ? `/api/inquiries/?status_filter=${statusFilter.value}` : '/api/inquiries/'
    const res = await authFetch(url)
    if (res?.ok) inquiries.value = await res.json()
  } finally {
    loadingData.value = false
  }
}

const changeStatus = async (inq, newStatus) => {
  const res = await authFetch(`/api/inquiries/${inq.id}/status?new_status=${newStatus}`, { method: 'PATCH' })
  if (res?.ok) {
    const updated = await res.json()
    const idx = inquiries.value.findIndex(i => i.id === inq.id)
    if (idx !== -1) inquiries.value[idx] = updated
  }
}

const openDetail = (inq) => { selectedInquiry.value = { ...inq } }

// --- Usuarios ---
const fetchUsers = async () => {
  const res = await authFetch('/api/users/')
  if (res?.ok) adminUsers.value = await res.json()
}

const createUser = async () => {
  userError.value = ''
  const res = await authFetch('/api/users/', { method: 'POST', body: JSON.stringify(newUser.value) })
  if (res?.ok) {
    adminUsers.value.push(await res.json())
    showNewUser.value = false
    newUser.value = { username: '', password: '', full_name: '', role: 'admin' }
  } else {
    const data = await res?.json().catch(() => ({}))
    userError.value = data?.detail || 'Error al crear usuario'
  }
}

// --- Partners ---
const fetchPartners = async () => {
  const res = await authFetch('/api/partners/')
  if (res?.ok) partners.value = await res.json()
}

const openPartnerModal = (partner = null) => {
  editingPartner.value = partner
  partnerForm.value = partner ? { ...partner } : emptyPartnerForm()
  partnerError.value = ''
  showPartnerModal.value = true
}

const savePartner = async () => {
  partnerError.value = ''
  const isEdit = !!editingPartner.value
  const url = isEdit ? `/api/partners/${editingPartner.value.id}` : '/api/partners/'
  const method = isEdit ? 'PUT' : 'POST'
  const res = await authFetch(url, { method, body: JSON.stringify(partnerForm.value) })
  if (res?.ok) {
    const saved = await res.json()
    if (isEdit) {
      const idx = partners.value.findIndex(p => p.id === saved.id)
      if (idx !== -1) partners.value[idx] = saved
    } else {
      partners.value.push(saved)
    }
    showPartnerModal.value = false
  } else {
    const data = await res?.json().catch(() => ({}))
    partnerError.value = data?.detail || 'Error al guardar partner'
  }
}

const deletePartner = async (partner) => {
  if (!confirm(`¿Eliminar a "${partner.name}"?`)) return
  const res = await authFetch(`/api/partners/${partner.id}`, { method: 'DELETE' })
  if (res?.ok || res?.status === 204) {
    partners.value = partners.value.filter(p => p.id !== partner.id)
  }
}

// --- General ---
const handleLogout = () => { logout(); router.push({ name: 'admin-login' }) }

const formatDate = (d) => {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('es-CL', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

const statusLabel    = (s) => ({ pending: 'Pendiente', quoted: 'Cotizado', closed: 'Cerrado' }[s])
const statusBtnClass = (s) => ({
  pending: 'border-amber-200 text-amber-700 hover:bg-amber-50',
  quoted:  'border-blue-200 text-[#0055A5] hover:bg-blue-50',
  closed:  'border-slate-200 text-slate-600 hover:bg-slate-50',
}[s])

onMounted(() => {
  fetchInquiries()
  fetchUsers()
  fetchPartners()
})
</script>

<script>
const StatusBadge = {
  props: ['status'],
  template: `
    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold"
      :class="{
        'bg-amber-100 text-amber-700': status === 'pending',
        'bg-blue-100 text-blue-700':   status === 'quoted',
        'bg-slate-100 text-slate-500': status === 'closed',
      }">
      {{ { pending: '● Pendiente', quoted: '● Cotizado', closed: '● Cerrado' }[status] }}
    </span>
  `,
}

const AgentBadge = {
  props: ['agent_status'],
  template: `
    <span v-if="agent_status" class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium"
      :class="{
        'bg-slate-100 text-slate-400':   agent_status === 'queued',
        'bg-violet-100 text-violet-700': agent_status === 'processing',
        'bg-green-100 text-green-700':   agent_status === 'quoted',
        'bg-amber-100 text-amber-700':   agent_status === 'awaiting_manual',
        'bg-orange-100 text-orange-700': agent_status === 'no_partners',
      }">
      <span v-if="agent_status === 'processing'" class="w-1.5 h-1.5 rounded-full bg-violet-500 animate-pulse"/>
      {{ {
        queued:          '⏳ En cola',
        processing:      '🤖 Cotizando',
        quoted:          '✅ Enviado',
        awaiting_manual: '✍️ Manual',
        no_partners:     '⚠️ Sin partners',
      }[agent_status] || agent_status }}
    </span>
    <span v-else class="text-slate-300 text-xs">—</span>
  `,
}

export default { components: { StatusBadge, AgentBadge } }
</script>
