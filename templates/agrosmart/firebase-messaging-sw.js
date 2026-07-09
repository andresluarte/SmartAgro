importScripts('https://www.gstatic.com/firebasejs/10.13.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.13.0/firebase-messaging-compat.js');

firebase.initializeApp({
  apiKey: "AIzaSyDm14bjY6JRtYBO23WFZD9PMbjHFI8-16I",
  authDomain: "smartagro-iot-7b768.firebaseapp.com",
  projectId: "smartagro-iot-7b768",
  storageBucket: "smartagro-iot-7b768.firebasestorage.app",
  messagingSenderId: "726241683195",
  appId: "1:726241683195:web:8ebff55ce9f8a9d1f6b25e"
});

const messaging = firebase.messaging();

messaging.onBackgroundMessage((payload) => {
  const { title, body } = payload.notification;
  self.registration.showNotification(title, {
    body: body,
    icon: '/static/agrosmart/img/logo.png'
  });
});