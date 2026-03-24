import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { searchMovies } from '../api/movieApi';

interface Movie {
  id: number;
  title: string;
  overview: string;
  poster_url: string | null;
  release_date: string;
  vote_average: number;
}

export default function SearchPage() {
  const [query, setQuery] = useState('');
  const [movies, setMovies] = useState<Movie[]>([]);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const data = await searchMovies(query);
      setMovies(data);
    } catch {
      alert('검색 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className={`min-h-[calc(100vh-140px)] bg-[#0d0d0d] text-white flex flex-col items-center px-4 ${
        movies.length === 0 ? 'justify-center' : 'pt-10 pb-16'
      }`}
    >
      <div className="w-full max-w-2xl">

        {/* 타이틀 — 검색 결과 없을 때만 크게 가운데 표시 */}
        {movies.length === 0 && (
          <div className="text-center mb-10">
            <h1 className="text-4xl font-bold text-[#00ff88] mb-2">🎬 FILM</h1>
            <p className="text-gray-500 text-sm">영화를 검색하고 리뷰를 남겨보세요</p>
          </div>
        )}

        {/* 검색창 */}
        <div className="flex gap-3 mb-8">
          <input
            className="flex-1 bg-[#1a1a1a] text-white px-5 py-3 rounded-lg text-base outline-none placeholder-gray-600 focus:ring-2 focus:ring-[#00ff88] transition border border-[#333]"
            type="text"
            placeholder="영화 제목을 검색하세요"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
          />
          <button
            className="bg-[#00ff88] hover:bg-[#00cc6a] text-black px-6 py-3 rounded-lg text-base font-bold transition-colors"
            onClick={handleSearch}
          >
            검색
          </button>
        </div>

        {/* 로딩 */}
        {loading && (
          <p className="text-gray-400 text-center text-sm mb-8">검색 중...</p>
        )}

        {/* 영화 카드 그리드 */}
        <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-4">
          {movies.map((movie) => (
            <div
              key={movie.id}
              className="bg-[#1a1a1a] rounded-lg overflow-hidden cursor-pointer hover:scale-105 hover:ring-2 hover:ring-[#00ff88] transition-all duration-200 border border-[#222]"
              onClick={() => navigate(`/movie/${movie.id}`)}
            >
              {movie.poster_url ? (
                <img
                  src={movie.poster_url}
                  alt={movie.title}
                  className="w-full aspect-[2/3] object-cover"
                />
              ) : (
                <div className="w-full aspect-[2/3] bg-[#333] flex items-center justify-center text-gray-500 text-xs">
                  포스터 없음
                </div>
              )}
              <div className="p-2">
                <h3 className="text-xs font-semibold mb-1 line-clamp-2">{movie.title}</h3>
                <p className="text-xs text-gray-500 mb-1">{movie.release_date}</p>
                <p className="text-xs text-yellow-400">⭐ {movie.vote_average.toFixed(1)}</p>
              </div>
            </div>
          ))}
        </div>

      </div>
    </div>
  );
}
