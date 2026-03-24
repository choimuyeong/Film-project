import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || '/api',
});

// 영화 검색
export const searchMovies = async (query: string) => {
  const response = await api.get('/movies/search', { params: { q: query } });
  return response.data;
};

// 영화 상세 조회
export const getMovieDetail = async (movieId: number) => {
  const response = await api.get(`/movies/${movieId}`);
  return response.data;
};

// 리뷰 목록 조회
export const getReviews = async (movieId: number) => {
  const response = await api.get(`/reviews/${movieId}`);
  return response.data;
};

// 리뷰 작성
export const createReview = async (data: {
  movie_id: number;
  movie_title: string;
  author: string;
  content: string;
  rating: number;
}) => {
  const response = await api.post('/reviews/', data);
  return response.data;
};
