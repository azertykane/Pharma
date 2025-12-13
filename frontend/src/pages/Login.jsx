const submit = async (e) => {
  e.preventDefault();
  setError(null);

  try {
    const form = new URLSearchParams();
    form.append("username", username);
    form.append("password", password);

    const res = await api.post("/users/login", form, {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    });

    onLogin(res.data.access_token);
  } catch (err) {
    setError("Identifiants incorrects");
  }
};
