<!-- src/features/plants/components/PlantGallery.vue -->
<template>
    <div class="plant-gallery">
      <!-- Main image -->
      <div class="main-image-container mb-3 position-relative shadow rounded overflow-hidden">
        <img 
          v-if="mainImage" 
          :src="mainImage.url" 
          :alt="mainImage.alt || 'Plant image'" 
          class="main-image w-100 h-100 object-fit-cover"
          @error="handleImageError"
        >
        <div v-else class="no-image d-flex align-items-center justify-content-center bg-light text-muted">
          <div class="text-center">
            <i class="bi bi-image display-3"></i>
            <p class="mt-2">No image available</p>
          </div>
        </div>
        
        <!-- Navigation arrows -->
        <button 
          v-if="images.length > 1" 
          class="gallery-nav gallery-nav-prev" 
          @click="prevImage"
          aria-label="Previous image"
        >
          <i class="bi bi-chevron-left"></i>
        </button>
        <button 
          v-if="images.length > 1" 
          class="gallery-nav gallery-nav-next" 
          @click="nextImage"
          aria-label="Next image"
        >
          <i class="bi bi-chevron-right"></i>
        </button>
        
        <!-- Indicators (dots) -->
        <div v-if="images.length > 1" class="gallery-indicators">
          <button 
            v-for="(image, index) in images" 
            :key="index" 
            class="indicator" 
            :class="{ active: index === currentIndex }"
            @click="setCurrentImage(index)"
            :aria-label="`Image ${index + 1}`"
          ></button>
        </div>
      </div>
      
      <!-- Thumbnails -->
      <div v-if="images.length > 1" class="thumbnails-container">
        <div class="row g-2">
          <div 
            v-for="(image, index) in images" 
            :key="index" 
            class="col-3 col-md-2"
          >
            <div 
              class="thumbnail-wrapper rounded overflow-hidden cursor-pointer"
              :class="{ 'active': index === currentIndex }"
              @click="setCurrentImage(index)"
            >
              <img 
                :src="image.thumbnail_url || image.url" 
                :alt="`Thumbnail ${index + 1}`" 
                class="thumbnail w-100 h-100 object-fit-cover"
                @error="handleThumbnailError($event, index)"
              >
            </div>
          </div>
        </div>
      </div>
      
      <!-- Fullscreen image modal -->
      <div 
        class="modal fade" 
        id="imageModal" 
        tabindex="-1" 
        aria-labelledby="imageModalLabel" 
        aria-hidden="true"
        ref="imageModal"
      >
        <div class="modal-dialog modal-dialog-centered modal-xl">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title" id="imageModalLabel">
                {{ currentImage && currentImage.title ? currentImage.title : 'Image Preview' }}
              </h5>
              <button 
                type="button" 
                class="btn-close" 
                data-bs-dismiss="modal" 
                aria-label="Close"
              ></button>
            </div>
            <div class="modal-body p-0 position-relative">
              <img 
                v-if="currentImage" 
                :src="currentImage.url" 
                class="modal-image w-100" 
                alt="Enlarged image"
              >
              
              <!-- Navigation arrows in modal -->
              <button 
                v-if="images.length > 1" 
                class="gallery-nav gallery-nav-prev" 
                @click.stop="prevImage"
                aria-label="Previous image"
              >
                <i class="bi bi-chevron-left"></i>
              </button>
              <button 
                v-if="images.length > 1" 
                class="gallery-nav gallery-nav-next" 
                @click.stop="nextImage"
                aria-label="Next image"
              >
                <i class="bi bi-chevron-right"></i>
              </button>
            </div>
            <div class="modal-footer">
              <small v-if="currentImage && currentImage.description" class="text-muted me-auto">
                {{ currentImage.description }}
              </small>
              <small class="text-muted">
                {{ currentIndex + 1 }} / {{ images.length }}
              </small>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
  
  const props = defineProps({
    images: {
      type: Array,
      default: () => []
    },
    initialIndex: {
      type: Number,
      default: 0
    }
  });
  
  const emit = defineEmits(['image-change']);
  
  // Modal reference
  const imageModal = ref(null);
  let modalInstance = null;
  
  // Current image index
  const currentIndex = ref(props.initialIndex);
  
  // Computed main image
  const mainImage = computed(() => {
    if (props.images.length === 0) return null;
    return props.images[currentIndex.value] || props.images[0];
  });
  
  // Computed current image (for modal)
  const currentImage = computed(() => {
    return mainImage.value;
  });
  
  // Set current image by index
  function setCurrentImage(index) {
    if (index >= 0 && index < props.images.length) {
      currentIndex.value = index;
      emit('image-change', index);
    }
  }
  
  // Go to previous image
  function prevImage() {
    const newIndex = currentIndex.value - 1;
    setCurrentImage(newIndex < 0 ? props.images.length - 1 : newIndex);
  }
  
  // Go to next image
  function nextImage() {
    const newIndex = currentIndex.value + 1;
    setCurrentImage(newIndex >= props.images.length ? 0 : newIndex);
  }
  
  // Handle main image loading error
  function handleImageError(event) {
    event.target.src = '/placeholder-plant.jpg'; // Replace with placeholder
  }
  
  // Handle thumbnail loading error
  function handleThumbnailError(event, index) {
    event.target.src = '/placeholder-plant-thumbnail.jpg'; // Replace with placeholder for thumbnails
  }
  
  // Handle keyboard navigation
  function handleKeyDown(event) {
    if (props.images.length <= 1) return;
    
    // Check if modal is open
    const isModalOpen = document.body.classList.contains('modal-open');
    
    if (isModalOpen || document.activeElement === document.body) {
      if (event.key === 'ArrowLeft') {
        prevImage();
      } else if (event.key === 'ArrowRight') {
        nextImage();
      }
    }
  }
  
  // Initialize modal on mount
  onMounted(() => {
    // Add keyboard listener
    window.addEventListener('keydown', handleKeyDown);
    
    // Initialize Bootstrap modal
    if (typeof bootstrap !== 'undefined' && imageModal.value) {
      modalInstance = new bootstrap.Modal(imageModal.value);
      
      // Add click handler to main image to open modal
      const mainImageElement = document.querySelector('.main-image-container');
      if (mainImageElement) {
        mainImageElement.addEventListener('click', () => {
          if (props.images.length > 0) {
            modalInstance.show();
          }
        });
      }
    }
  });
  
  // Cleanup on unmount
  onUnmounted(() => {
    window.removeEventListener('keydown', handleKeyDown);
    
    // Dispose Bootstrap modal
    if (modalInstance) {
      modalInstance.dispose();
    }
  });
  
  // Watch initialIndex changes
  watch(() => props.initialIndex, (newIndex) => {
    setCurrentImage(newIndex);
  });
  
  // Watch images changes
  watch(() => props.images, (newImages) => {
    if (newImages.length === 0) {
      currentIndex.value = 0;
    } else if (currentIndex.value >= newImages.length) {
      currentIndex.value = newImages.length - 1;
    }
  }, { deep: true });
  </script>
  
  <style scoped>
  .plant-gallery {
    margin-bottom: 2rem;
  }
  
  .main-image-container {
    position: relative;
    height: 400px;
    cursor: pointer;
    background-color: #f8f9fa;
  }
  
  .main-image {
    transition: transform 0.5s ease;
  }
  
  .main-image-container:hover .main-image {
    transform: scale(1.02);
  }
  
  .no-image {
    height: 100%;
    width: 100%;
  }
  
  .gallery-nav {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    background-color: rgba(255, 255, 255, 0.7);
    border: none;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    cursor: pointer;
    opacity: 0;
    transition: opacity 0.3s ease, background-color 0.3s ease;
    z-index: 10;
  }
  
  .gallery-nav-prev {
    left: 10px;
  }
  
  .gallery-nav-next {
    right: 10px;
  }
  
  .main-image-container:hover .gallery-nav,
  .modal-body:hover .gallery-nav {
    opacity: 1;
  }
  
  .gallery-nav:hover {
    background-color: rgba(255, 255, 255, 0.9);
  }
  
  .gallery-indicators {
    position: absolute;
    bottom: 10px;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    gap: 8px;
    z-index: 10;
  }
  
  .indicator {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background-color: rgba(255, 255, 255, 0.5);
    border: none;
    padding: 0;
    cursor: pointer;
    transition: background-color 0.3s ease, transform 0.3s ease;
  }
  
  .indicator.active {
    background-color: white;
    transform: scale(1.2);
  }
  
  .thumbnails-container {
    margin-top: 10px;
  }
  
  .thumbnail-wrapper {
    height: 70px;
    overflow: hidden;
    border: 2px solid transparent;
    transition: border-color 0.3s ease, transform 0.3s ease;
    cursor: pointer;
  }
  
  .thumbnail-wrapper:hover {
    transform: translateY(-2px);
  }
  
  .thumbnail-wrapper.active {
    border-color: var(--bs-primary);
  }
  
  .thumbnail {
    transition: transform 0.3s ease;
  }
  
  .thumbnail-wrapper:hover .thumbnail {
    transform: scale(1.1);
  }
  
  .modal-image {
    max-height: 80vh;
    object-fit: contain;
  }
  
  .cursor-pointer {
    cursor: pointer;
  }
  
  /* Mobile responsiveness */
  @media (max-width: 768px) {
    .main-image-container {
      height: 300px;
    }
    
    .gallery-nav {
      width: 32px;
      height: 32px;
      font-size: 1.25rem;
      opacity: 0.8; /* Always visible on mobile */
    }
    
    .indicator {
      width: 8px;
      height: 8px;
    }
    
    .thumbnail-wrapper {
      height: 60px;
    }
  }
  </style>