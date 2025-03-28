import { initializeApp } from 'https://www.gstatic.com/firebasejs/9.6.8/firebase-app.js';
import {
    getAuth,
    onAuthStateChanged,
    signInWithEmailAndPassword,
    createUserWithEmailAndPassword,
    signOut
} from 'https://www.gstatic.com/firebasejs/9.6.8/firebase-auth.js';
import { getFirestore, setDoc, doc } from 'https://www.gstatic.com/firebasejs/9.6.8/firebase-firestore.js';
import { addDoc, collection } from 'https://www.gstatic.com/firebasejs/9.6.8/firebase-firestore.js';


const firebaseConfig = {
    apiKey: "AIzaSyBdOjj4fJUbSTMigivkN-nd4o4fOTHDH_w",
    authDomain: "esd-g3t1.firebaseapp.com",
    projectId: "esd-g3t1",
    storageBucket: "esd-g3t1.firebasestorage.app",
    messagingSenderId: "770389471915",
    appId: "1:770389471915:web:cad7a8b186b84befbefdee",
    measurementId: "G-BF0YB0C59V"
  };
  
// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);

const signUpButton = document.getElementById('signUp');
const signInButton = document.getElementById('signIn');
const container = document.getElementById('container');

signUpButton.addEventListener('click', () => {
	container.classList.add("right-panel-active");
});

signInButton.addEventListener('click', () => {
	container.classList.remove("right-panel-active");
});

//SIGNUP FUNCTION
document.getElementById("signup-form").addEventListener("submit", function (e) {
    e.preventDefault(); 

    const email = document.getElementById("signup-email").value;
    const password = document.getElementById("signup-password").value;
    const message = document.getElementById("signup-message");

    createUserWithEmailAndPassword(auth, email, password)
  .then(async (userCredential) => {
    const uid = userCredential.user.uid;
    message.innerText = "Signup Successful!";
    message.style.color = "green";

    await setDoc(doc(db, "users", uid), {
      displayName: "",
      darkMode: false
    });
    console.log("Default preferences saved for UID:", uid);
  })
  .catch((error) => {
    message.innerText = error.message;
    message.style.color = "red";
    console.error("Signup Error:", error);
  });

});

// LOGIN FUNCTION
document.getElementById("login-form").addEventListener("submit", function (e) {
    e.preventDefault(); 

    const email = document.getElementById("login-email").value;
    const password = document.getElementById("login-password").value;
    const message = document.getElementById("login-message");

    signInWithEmailAndPassword(auth, email, password)
        .then((userCredential) => {
            message.innerText = "Login Successful!";
            message.style.color = "green";
            const uid = userCredential.user.uid;
            console.log("User UID:", uid);
            console.log("User Logged In:", userCredential.user);
        })
        .catch((error) => {
            message.innerText = error.message;
            message.style.color = "red";
            console.error("Error:", error);
        });
});
