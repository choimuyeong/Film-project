import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getMovieDetail, getReviews } from '../api/movieApi';

interface Movie {
  id: number;
  title: string;
  overview: string;
  poster_url: string | null;
  release_date: string;
  vote_average: number;
  genres: string[];
  runtime: number | null;
  tagline: string | null;
}

interface Review {
  id: number;
  author: string;
  content: string;
  rating: number;
  sentiment: string | null;
  sentiment_score: number | null;
  created_at: string;
}

export default function DetailPage() {
  const { movieId } = useParams();
  const navigate = useNavigate();
  const [movie, setMovie] = useState<Movie | null>(null);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [movieData, reviewData] = await Promise.all([
          getMovieDetail(Number(movieId)),
          getReviews(Number(movieId)),
        ]);
        setMovie(movieData);
        setReviews(reviewData);
      } catch {
        alert('데이터를 불러오는 중 오류가 발생했습니다.');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [movieId]);

  if (loading) return (
    <div className="flex items-center justify-center min-h-[calc(100vh-140px)] bg-[#0d0d0d] text-white text-xl">
      불러오는 중...
    </div>
  );
  if (!movie) return (
    <div className="flex items-center justify-center min-h-[calc(100vh-140px)] bg-[#0d0d0d] text-white text-xl">
      영화를 찾을 수 없습니다.
    </div>
  );

  return (
    <div className="min-h-[calc(100vh-140px)] bg-[#0d0d0d] text-white px-4 py-8">
      <div className="w-full max-w-5xl mx-auto">
        {/* 영화 정보 */}
        <div className="flex flex-col md:flex-row gap-8 md:gap-10 mb-16 items-start">
          {movie.poster_url && (
            <img
              src={movie.poster_url}
              alt={movie.title}
              className="w-56 rounded-lg flex-shrink-0 shadow-2xl mx-auto md:mx-0"
            />
          )}
          <div className="flex-1">
            <h1 className="text-4xl font-bold mb-3 text-center md:text-left">{movie.title}</h1>
            {movie.tagline && (
              <p className="text-gray-400 italic mb-4 text-center md:text-left">"{movie.tagline}"</p>
            )}
            <div className="flex flex-wrap gap-4 md:gap-6 text-gray-300 mb-4 justify-center md:justify-start">
              <span>📅 {movie.release_date}</span>
              <span>⭐ {movie.vote_average.toFixed(1)}</span>
              {movie.runtime && <span>⏱ {movie.runtime}분</span>}
            </div>
            <div className="flex gap-2 flex-wrap mb-5 justify-center md:justify-start">
              {movie.genres.map((g) => (
                <span key={g} className="bg-[#333] px-3 py-1 rounded-full text-sm">
                  {g}
                </span>
              ))}
            </div>
            <p className="text-gray-300 leading-relaxed mb-6 text-center md:text-left">{movie.overview}</p>
            <div className="flex justify-center md:justify-start">
              <button
                className="bg-[#0d0d0d] hover:bg-[#b2070f] text-white px-7 py-3 rounded text-base font-semibold transition-colors border border-[#333]"
                onClick={() => navigate(`/movie/${movieId}/review`)}
              >
                리뷰 작성하기
              </button>
            </div>
          </div>
        </div>

        {/* 리뷰 목록 */}
        <div className="border-t border-[#333] pt-10">
          <h2 className="text-2xl font-bold mb-6 text-center md:text-left">리뷰 ({reviews.length})</h2>
          {reviews.length === 0 ? (
            <p className="text-gray-400 text-center md:text-left">아직 리뷰가 없어요. 첫 번째 리뷰를 작성해보세요!</p>
          ) : (
            <div className="flex flex-col gap-4">
              {reviews.map((review) => (
                <div key={review.id} className="bg-[#1f1f1f] rounded-lg p-5 border border-[#2a2a2a]">
                  <div className="flex items-center gap-3 mb-3 flex-wrap">
                    <span className="font-bold text-base">{review.author}</span>
                    <span className="text-yellow-400">⭐ {review.rating}</span>
                    {review.sentiment && (
                      <span className={`px-3 py-1 rounded-full text-xs text-white font-semibold ${
                        review.sentiment === 'positive' ? 'bg-green-600' : 'bg-[#0d0d0d]'
                      }`}>
                        {review.sentiment === 'positive' ? '긍정' : '부정'}
                        {review.sentiment_score &&
                          ` ${(review.sentiment_score * 100).toFixed(0)}%`}
                      </span>
                    )}
                  </div>
                  <p className="text-gray-300 leading-relaxed mb-2">{review.content}</p>
                  <p className="text-gray-600 text-sm">
                    {new Date(review.created_at).toLocaleDateString('ko-KR')}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
