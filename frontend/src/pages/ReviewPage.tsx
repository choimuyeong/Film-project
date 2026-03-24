import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { createReview } from '../api/movieApi';

export default function ReviewPage() {
  const { movieId, movieTitle } = useParams();
  const navigate = useNavigate();
  const [author, setAuthor] = useState('');
  const [content, setContent] = useState('');
  const [rating, setRating] = useState(5.0);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!author.trim() || !content.trim()) {
      alert('작성자와 리뷰 내용을 입력해주세요.');
      return;
    }
    if (content.length < 10) {
      alert('리뷰 내용을 10자 이상 입력해주세요.');
      return;
    }
    setLoading(true);
    try {
      await createReview({
        movie_id: Number(movieId),
        movie_title: decodeURIComponent(movieTitle || ''),
        author,
        content,
        rating,
      });
      alert('리뷰가 등록됐어요!');
      navigate(`/movie/${movieId}`);
    } catch {
      alert('리뷰 등록 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-140px)] bg-[#0d0d0d] text-white px-4 py-8">
      <div className="w-full max-w-3xl mx-auto">
        {/* 뒤로가기 */}
        <button
          className="text-gray-400 hover:text-white transition-colors mb-6 text-base"
          onClick={() => navigate(-1)}
        >
          ← 돌아가기
        </button>

        <h2 className="text-3xl font-bold mb-2 text-center md:text-left">리뷰 작성</h2>
        <p className="text-[#00ff88] text-lg mb-8 text-center md:text-left">
          {decodeURIComponent(movieTitle || '')}
        </p>

        <div className="max-w-xl mx-auto md:mx-0 flex flex-col gap-5">
          {/* 작성자 */}
          <div className="flex flex-col gap-2">
            <label className="text-sm text-gray-400">작성자</label>
            <input
              className="bg-[#333] text-white px-4 py-3 rounded outline-none focus:ring-2 focus:ring-[#00ff88] transition placeholder-gray-500 border border-[#444]"
              type="text"
              placeholder="닉네임을 입력하세요"
              value={author}
              onChange={(e) => setAuthor(e.target.value)}
            />
          </div>

          {/* 별점 */}
          <div className="flex flex-col gap-2">
            <label className="text-sm text-gray-400">별점</label>
            <select
              className="bg-[#333] text-white px-4 py-3 rounded outline-none focus:ring-2 focus:ring-[#00ff88] transition cursor-pointer border border-[#444]"
              value={rating}
              onChange={(e) => setRating(Number(e.target.value))}
            >
              {[1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0].map((r) => (
                <option key={r} value={r}>⭐ {r}</option>
              ))}
            </select>
          </div>

          {/* 리뷰 내용 */}
          <div className="flex flex-col gap-2">
            <label className="text-sm text-gray-400">리뷰 내용</label>
            <textarea
              className="bg-[#333] text-white px-4 py-3 rounded outline-none focus:ring-2 focus:ring-[#00ff88] transition placeholder-gray-500 resize-vertical border border-[#444]"
              placeholder="영화에 대한 감상을 자유롭게 작성해주세요 (최소 10자)"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              rows={6}
            />
            <p className={`text-sm text-right ${content.length < 10 ? 'text-[#00ff88]' : 'text-gray-500'}`}>
              {content.length} / 1000자
            </p>
          </div>

          {/* 제출 버튼 */}
          <button
            className="bg-[#0d0d0d] hover:bg-[#b2070f] disabled:bg-gray-600 disabled:cursor-not-allowed text-white py-4 rounded text-base font-semibold transition-colors mt-2 border border-[#333]"
            onClick={handleSubmit}
            disabled={loading}
          >
            {loading ? '감성 분석 중...' : '리뷰 등록하기'}
          </button>
        </div>
      </div>
    </div>
  );
}
