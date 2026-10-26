import streamlit as st
st.title('나의 첫 웹 서비스 만들기!')
a=st.text_input('이름을 입력해 주세요!')
b=st.selectbox('좋아하는 음식을 선택해주세요!',['곱창','스테이크','떡볶이'])
if st.button('인사말 생성'):
  st.write('반갑습니다!')
  st.info(a+'새꺄!!! 반갑다!')
  st.warning(b+'야! 너도? 나도 갸좋아함!')
  st.error('우리 이제 깐부임 ㅋㅋㅋ')
  st.balloons()
