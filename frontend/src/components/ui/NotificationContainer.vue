<template>
  <Teleport to="body">
    <div class="notification-container">
      <NotificationToast
        v-for="notification in notifications"
        :key="notification.id"
        :type="notification.type"
        :title="notification.title"
        :message="notification.message"
        :duration="notification.duration"
        :auto-close="notification.autoClose"
        @close="removeNotification(notification.id)"
      />
    </div>
  </Teleport>
</template>

<script>
import { computed } from 'vue'
import { useNotificationStore } from '@/stores/notificationStore'
import NotificationToast from './NotificationToast.vue'

export default {
  name: 'NotificationContainer',
  components: {
    NotificationToast
  },
  setup() {
    const notificationStore = useNotificationStore()
    
    const notifications = computed(() => notificationStore.notifications)
    
    const removeNotification = (id) => {
      notificationStore.removeNotification(id)
    }
    
    return {
      notifications,
      removeNotification
    }
  }
}
</script>

<style scoped>
.notification-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  pointer-events: none;
}

.notification-container > * {
  pointer-events: auto;
}

@media (max-width: 768px) {
  .notification-container {
    top: 10px;
    right: 10px;
    left: 10px;
  }
}
</style>
