(async function handleYape () {
  const otp = docment.getElementById("form-checkout__payerOTP").value;
  const phoneNumber = docment.getElementById("form-checkout__payerPhone").value;
  const yapeOptions = {
    otp,
    phoneNumber
  };
  const yape = mp.yape(yapeOptions);
  const yapeToken = await yape.create();
  return yapeToken;
});