require 'json'

module Jekyll
  class MarketPageGenerator < Generator
    safe true
    priority :normal

    REGION_SLUGS = {
      '경기도' => 'gyeonggi', '인천' => 'incheon', '강원도' => 'gangwon',
      '충청북도' => 'chungbuk', '충청남도' => 'chungnam',
      '전라북도' => 'jeonbuk', '전라남도' => 'jeonnam',
      '경상북도' => 'gyeongbuk', '경상남도' => 'gyeongnam',
      '대구' => 'daegu', '울산' => 'ulsan', '부산' => 'busan',
      '광주' => 'gwangju', '세종' => 'sejong', '대전' => 'daejeon',
      '제주도' => 'jeju', '서울' => 'seoul',
    }.freeze

    def generate(site)
      markets = site.data['markets']
      return unless markets&.any?

      Jekyll.logger.info "MarketGenerator:", "#{markets.size}개 시장 페이지 생성 중..."

      markets.each do |market|
        same_region = markets
          .select { |m| m['region'] == market['region'] && m['id'] != market['id'] }
          .map { |m| { 'id' => m['id'], 'name' => m['name'], 'days_display' => days_full_label(m['days']) } }
          .first(8)

        days_key = market['days'].sort.join('-')
        same_days = markets
          .select { |m| m['days'].sort.join('-') == days_key && m['id'] != market['id'] }
          .map { |m| { 'id' => m['id'], 'name' => m['name'], 'region' => m['region'], 'city' => m['city'] } }
          .first(8)

        site.pages << MarketPage.new(site, market, same_region, same_days)
      end

      by_region = markets.group_by { |m| m['region'] }
      by_region.each do |region, region_markets|
        slug = REGION_SLUGS[region] || region
        site.pages << RegionPage.new(site, region, slug, region_markets)
      end

      by_days = {}
      markets.each do |m|
        key = m['days'].sort.join('-')
        by_days[key] ||= []
        by_days[key] << m
      end
      by_days.each do |days_key, day_markets|
        site.pages << DaysPage.new(site, days_key, day_markets)
      end

      site.pages << SearchIndexPage.new(site, markets)

      Jekyll.logger.info "MarketGenerator:", "완료 (#{markets.size}개 시장)"
    end

    private

    def days_full_label(days)
      base = days.min
      all = []
      d = base
      while d <= 30
        all << d
        d += 5
      end
      all.sort.join('·') + "일"
    end
  end

  class MarketPage < Page
    REGION_SLUGS = MarketPageGenerator::REGION_SLUGS

    def initialize(site, market, same_region, same_days)
      @site = site
      @base = site.source
      @dir  = "market/#{market['id']}"
      @name = 'index.html'

      self.process(@name)
      self.read_yaml(File.join(@base, '_layouts'), 'market.html')
      self.data.merge!(market)
      self.data['layout']        = 'market'
      self.data['same_region']   = same_region
      self.data['same_days']     = same_days
      self.data['days_key']      = market['days'].sort.join('-')
      self.data['days_display']  = days_full_label(market['days'])
      self.data['region_slug']   = REGION_SLUGS[market['region']] || market['region']
      self.data['title']         = "#{market['name']} 장날 특산물 오시는길 | 우아시장"
      self.data['description']   = market['seo_description'] ||
        "#{market['name']}(#{market['region']} #{market['city']}) 장날 #{days_full_label(market['days'])}, 특산물, 찾아가는 길 안내."
    end

    private

    def days_full_label(days)
      base = days.min
      all = []
      d = base
      while d <= 30
        all << d
        d += 5
      end
      all.sort.join('·') + "일"
    end
  end

  class RegionPage < Page
    def initialize(site, region, slug, markets)
      @site = site
      @base = site.source
      @dir  = "region/#{slug}"
      @name = 'index.html'

      self.process(@name)
      self.read_yaml(File.join(@base, '_layouts'), 'region.html')
      self.data['layout']      = 'region'
      self.data['region']      = region
      self.data['region_slug'] = slug
      self.data['markets']     = markets
      self.data['title']       = "#{region} 오일장 목록 | 우아시장"
      self.data['description'] = "#{region}의 전통 5일장(오일장) #{markets.size}개 목록. 장날과 특산물 정보를 확인하세요."
    end
  end

  class DaysPage < Page
    def initialize(site, days_key, markets)
      @site = site
      @base = site.source
      @dir  = "days/#{days_key}"
      @name = 'index.html'

      self.process(@name)
      self.read_yaml(File.join(@base, '_layouts'), 'days.html')

      days = days_key.split('-').map(&:to_i).sort
      label = days.join('·') + "일장"

      self.data['layout']     = 'days'
      self.data['days_key']   = days_key
      self.data['days_label'] = label
      self.data['markets']    = markets
      self.data['title']      = "#{label} 전국 오일장 목록 | 우아시장"
      self.data['description'] = "전국 #{label}이 열리는 전통시장 #{markets.size}개 목록과 장날 정보."
    end
  end

  class SearchIndexPage < Page
    def initialize(site, markets)
      @site = site
      @base = site.source
      @dir  = ''
      @name = 'search_index.json'

      self.process(@name)
      self.data = { 'layout' => nil, 'sitemap' => false }

      index = markets.map do |m|
        {
          'id'          => m['id'],
          'name'        => m['name'],
          'region'      => m['region'],
          'city'        => m['city'],
          'days'        => m['days'],
          'specialties' => m['specialties'],
          'address'     => m['address'],
        }
      end

      self.content = index.to_json
    end

    def output   = self.content
    def render(layouts, registers); end
  end
end
