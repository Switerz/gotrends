"""
Gera o relatório de análise Kokeshi em PDF usando fpdf2.
"""
from fpdf import FPDF
from datetime import date


class KokeshiReport(FPDF):
    BRAND_RED = (180, 40, 40)
    DARK = (30, 30, 30)
    GRAY = (100, 100, 100)
    LIGHT_GRAY = (240, 240, 240)
    MID_GRAY = (200, 200, 200)
    WHITE = (255, 255, 255)
    GREEN = (34, 139, 34)
    ORANGE = (200, 100, 0)
    RED_CELL = (200, 50, 50)

    _FONTS_ADDED = False

    def _ensure_fonts(self):
        if KokeshiReport._FONTS_ADDED:
            return
        import os
        win_fonts = "C:/Windows/Fonts/"
        self.add_font("Arial", "",  win_fonts + "arial.ttf")
        self.add_font("Arial", "B", win_fonts + "arialbd.ttf")
        self.add_font("Arial", "I", win_fonts + "ariali.ttf")
        self.add_font("Arial", "BI", win_fonts + "arialbi.ttf")
        KokeshiReport._FONTS_ADDED = True

    def header(self):
        self._ensure_fonts()
        self.set_fill_color(*self.BRAND_RED)
        self.rect(0, 0, 210, 14, "F")
        self.set_font("Arial", "B", 11)
        self.set_text_color(*self.WHITE)
        self.set_xy(10, 3)
        self.cell(0, 8, "KOKESHI — Analise Google Ads | Ultimos 30 dias", align="L")
        self.set_xy(0, 3)
        self.cell(200, 8, "24/04/2026", align="R")
        self.ln(16)

    def footer(self):
        self.set_y(-12)
        self.set_font("Arial", "", 8)
        self.set_text_color(*self.GRAY)
        self.cell(0, 8, f"Gerado automaticamente pelo agente Google Ads Growth — Pagina {self.page_no()}", align="C")

    def section_title(self, text, color=None):
        if color is None:
            color = self.BRAND_RED
        self.set_font("Arial", "B", 12)
        self.set_text_color(*color)
        self.set_fill_color(*self.LIGHT_GRAY)
        self.cell(0, 8, f"  {text}", ln=True, fill=True)
        self.set_text_color(*self.DARK)
        self.ln(2)

    def sub_title(self, text):
        self.set_font("Arial", "B", 10)
        self.set_text_color(*self.DARK)
        self.cell(0, 7, text, ln=True)
        self.ln(1)

    def body(self, text):
        self.set_font("Arial", "", 9)
        self.set_text_color(*self.DARK)
        self.multi_cell(0, 5, text)
        self.ln(1)

    def note(self, text):
        self.set_font("Arial", "I", 8)
        self.set_text_color(*self.GRAY)
        self.multi_cell(0, 5, text)
        self.ln(1)

    def alert_box(self, text, color=None):
        if color is None:
            color = (255, 243, 205)
        self.set_fill_color(*color)
        self.set_draw_color(200, 160, 0)
        self.set_font("Arial", "B", 9)
        self.set_text_color(100, 70, 0)
        self.multi_cell(0, 6, f"  [!]  {text}", border=1, fill=True)
        self.set_text_color(*self.DARK)
        self.ln(3)

    def kpi_row(self, items):
        """items = list of (label, value, color)"""
        col_w = 190 / len(items)
        x0 = self.get_x()
        y0 = self.get_y()
        for label, value, color in items:
            self.set_fill_color(*self.LIGHT_GRAY)
            self.set_draw_color(*self.MID_GRAY)
            self.rect(x0, y0, col_w - 2, 18, "FD")
            self.set_xy(x0 + 2, y0 + 1)
            self.set_font("Arial", "", 7)
            self.set_text_color(*self.GRAY)
            self.cell(col_w - 4, 5, label)
            self.set_xy(x0 + 2, y0 + 7)
            self.set_font("Arial", "B", 11)
            self.set_text_color(*color)
            self.cell(col_w - 4, 8, value)
            x0 += col_w
        self.set_xy(self.l_margin, y0 + 20)
        self.set_text_color(*self.DARK)

    def table(self, headers, rows, col_widths=None, highlight_col=None):
        if col_widths is None:
            col_w = 190 / len(headers)
            col_widths = [col_w] * len(headers)

        # header row
        self.set_fill_color(*self.BRAND_RED)
        self.set_text_color(*self.WHITE)
        self.set_font("Arial", "B", 7)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 6, f" {h}", border=0, fill=True)
        self.ln()

        self.set_font("Arial", "", 7)
        for ri, row in enumerate(rows):
            bg = self.WHITE if ri % 2 == 0 else (248, 248, 248)
            self.set_fill_color(*bg)
            self.set_text_color(*self.DARK)
            row_h = 5
            for ci, cell in enumerate(row):
                val = str(cell)
                # colour special cells
                if highlight_col and ci == highlight_col:
                    try:
                        num = float(val.replace("R$", "").replace(",", ".").replace("%", ""))
                        if num <= 20:
                            self.set_text_color(*self.GREEN)
                        elif num <= 40:
                            self.set_text_color(180, 120, 0)
                        else:
                            self.set_text_color(*self.RED_CELL)
                    except:
                        pass
                self.cell(col_widths[ci], row_h, f" {val}", border=0, fill=True)
                self.set_text_color(*self.DARK)
            self.ln()
        self.set_draw_color(*self.MID_GRAY)
        self.set_line_width(0.3)
        self.ln(2)

    def opportunity_box(self, label, value, sub=None):
        self.set_fill_color(*self.LIGHT_GRAY)
        self.set_draw_color(*self.MID_GRAY)
        self.set_font("Arial", "B", 9)
        self.set_text_color(*self.DARK)
        x = self.get_x()
        y = self.get_y()
        self.rect(x, y, 188, 14, "FD")
        self.set_xy(x + 3, y + 2)
        self.cell(120, 5, label)
        self.set_font("Arial", "B", 12)
        self.set_text_color(*self.GREEN)
        self.set_xy(x + 130, y + 1)
        self.cell(55, 7, value, align="R")
        if sub:
            self.set_xy(x + 3, y + 8)
            self.set_font("Arial", "I", 7)
            self.set_text_color(*self.GRAY)
            self.cell(180, 4, sub)
        self.set_xy(self.l_margin, y + 16)
        self.set_text_color(*self.DARK)


def build_pdf():
    pdf = KokeshiReport(orientation="P", unit="mm", format="A4")
    pdf.set_margins(10, 18, 10)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf._ensure_fonts()
    pdf.add_page()

    # ── ALERTA ──────────────────────────────────────────────────────────────────
    pdf.alert_box(
        "LANÇAMENTO IMINENTE: Sérum Roll on Adeus Olheiras (abr/26) e 4 lançamentos em mai/26 "
        "(Bastão Adeus Poros, Creme Antioleosidade, Antissinais, Dia das Mães). "
        "Keywords ainda não criadas na conta. Ver Seção 7."
    )

    # ── 1. RESUMO EXECUTIVO ──────────────────────────────────────────────────────
    pdf.section_title("1. Resumo Executivo")
    pdf.kpi_row([
        ("Custo total", "R$103.510", pdf.DARK),
        ("Conversões", "8.741", pdf.DARK),
        ("CPA médio", "R$11,84", pdf.GREEN),
        ("Receita estimada", "R$786.719", pdf.GREEN),
        ("ROAS estimado", "7,60x", pdf.GREEN),
    ])

    pdf.sub_title("Mapa de oportunidade financeira")
    pdf.opportunity_box(
        "Escalar winners (CPA ≤R$15) com +50% de spend",
        "+R$40.738",
        "Terms branded com ROAS 10–47x têm headroom via redução de tROAS-alvo"
    )
    pdf.ln(1)
    pdf.opportunity_box(
        "Cortar desperdício e realocar (CPA >R$40) — cenário base",
        "+R$4.240",
        "R$743 em spend ineficiente, oportunidade de receita recuperável de R$4.449"
    )
    pdf.ln(3)
    pdf.note(
        "A principal alavanca é escalar o que funciona (+R$40k), não cortar o que não funciona (+R$4k).\n"
        "Forecasts de curte desperdício: conservador +R$1.015 | base +R$4.240 | otimista +R$5.653"
    )

    # ── 2. BRANDED ───────────────────────────────────────────────────────────────
    pdf.section_title("2. Branded — Motor da conta")
    pdf.body(
        "Perda de orçamento = 0% em todos os termos. Restrição é Ad Rank / tROAS, não budget.\n"
        "Para escalar: reduzir tROAS-alvo 10–15%/semana nos termos com ROAS atual muito acima do target."
    )
    pdf.table(
        ["Termo", "CPA", "ROAS", "Custo", "Conv", "Ação"],
        [
            ["site kokeshi",             "R$1,90",  "47,3x", "R$72",    "37,9",  "Reduzir tROAS"],
            ["kokeshi cosméticos",        "R$2,84",  "31,7x", "R$857",   "302",   "Reduzir tROAS"],
            ["kokeshi",                   "R$3,26",  "27,6x", "R$7.431", "2.279", "Reduzir tROAS"],
            ["kokeshi site oficial",      "R$3,93",  "22,9x", "R$84",    "21,5",  "Reduzir tROAS"],
            ["kokeshi creme",             "R$5,29",  "17,0x", "R$87",    "16,5",  "Escalar"],
            ["kokeshi pele de porcelana", "R$5,57",  "16,1x", "R$223",   "40",    "Escalar"],
            ["pele de porcelana kokeshi", "R$8,85",  "10,2x", "R$90",    "10,2",  "Escalar"],
            ["creme kokeshi",             "R$9,14",  "9,8x",  "R$111",   "12,2",  "Escalar"],
            ["produtos kokeshi",          "R$9,32",  "9,7x",  "R$112",   "12",    "Escalar"],
            ["kokeshi é bom",             "R$12,17", "7,4x",  "R$1.080", "88,7",  "Manter"],
            ["gota de colageno kokeshi",  "R$16,20", "5,6x",  "R$44",    "2,7",   "Manter"],
            ["kokeshi reclame aqui",      "R$16,36", "5,5x",  "R$173",   "10,6",  "Manter *"],
        ],
        col_widths=[58, 18, 16, 18, 16, 28],
        highlight_col=1,
    )
    pdf.note(
        "* 'kokeshi reclame aqui' converte com CPA R$16 e 10,6 conversões — usuário que chega com dúvida "
        "de reputação está comprando. Sinal positivo de confiança da marca. Manter cobertura total."
    )

    # ── 3. NON-BRANDED CORTAR ────────────────────────────────────────────────────
    pdf.section_title("3. Non-Branded — Negativar agora")
    pdf.table(
        ["Termo", "CPA", "Custo", "Conv", "ROAS", "Onde negativar"],
        [
            ["produtos coreanos para pele", "R$360,73", "R$54,41", "0,15", "0,25x",
             "Search Soluções → search | produtos coreanos para pele"],
            ["creamy",                       "R$59,64",  "R$59,64", "1,0",  "1,51x",
             "Shopping Best Sellers"],
        ],
        col_widths=[42, 22, 18, 14, 16, 78],
        highlight_col=1,
    )
    pdf.note("Estes dois termos liberam R$114 para realocar. 'Produtos coreanos para pele' tem ROAS 0,25x — pior termo da conta.")

    # ── 4. NON-BRANDED REVISAR ───────────────────────────────────────────────────
    pdf.section_title("4. Non-Branded — Revisar urgente (produto errado no Shopping)")
    pdf.table(
        ["Termo", "CPA", "Custo", "Conv", "ROAS"],
        [
            ["skin care coreano",       "R$44,84", "R$137,80", "3,07", "2,01x"],
            ["pele de porcelana",        "R$44,33", "R$134,20", "3,03", "2,03x"],
            ["kit skincare",             "R$40,74", "R$122,21", "3,0",  "2,21x"],
            ["produtos kokeshi são bons","R$47,41", "R$47,43",  "1,0",  "1,90x"],
        ],
        col_widths=[60, 24, 24, 16, 24],
        highlight_col=1,
    )
    pdf.note(
        "Os três primeiros estão no mesmo grupo (Shopping Best Sellers). CPA >R$40 com termos de alto "
        "intent indica produto errado sendo exibido no feed. Verificar qual SKU está vinculado e ajustar "
        "prioridade."
    )

    # ── 5. NON-BRANDED ESCALAR ───────────────────────────────────────────────────
    pdf.section_title("5. Non-Branded — Escalar")
    pdf.table(
        ["Termo", "CPA", "ROAS", "Custo", "Conv"],
        [
            ["niacinamida",             "R$10,46", "8,6x", "R$37",  "3,6"],
            ["medicube (concorrente)",   "R$13,49", "6,7x", "R$63",  "4,7"],
            ["kikoshi (concorrente)",    "R$11,68", "7,7x", "R$35",  "3,0"],
            ["hidratante facial",        "R$15,13", "5,9x", "R$94",  "6,2"],
            ["creme para olheiras",      "R$18,26", "4,9x", "R$55",  "3,0"],
            ["creme para area dos olhos","R$18,69", "4,8x", "R$47",  "2,5"],
            ["produtos coreanos",        "R$16,22", "5,6x", "R$48",  "3,0"],
            ["skincare coreana",         "R$17,08", "5,3x", "R$34",  "2,0"],
            ["creme coreano para o rosto","R$19,17","4,7x", "R$38",  "2,0"],
            ["olhos de gueixa",          "R$22,01", "4,1x", "R$287", "13"],
        ],
        col_widths=[68, 22, 18, 18, 18],
        highlight_col=1,
    )
    pdf.note(
        "'olhos de gueixa' é o maior cluster non-branded (R$287 spend, 13 conv). Com o lançamento do "
        "Sérum Roll on Adeus Olheiras este mês, este grupo deve ganhar relevância adicional — bom momento para escalar."
    )

    # ── 6. ANOMALIA ──────────────────────────────────────────────────────────────
    pdf.section_title("6. Anomalia estrutural — kit pele de porcelana")
    pdf.table(
        ["Grupo", "Custo", "Conv", "CPA", "Ação"],
        [
            ["Shopping Best Sellers",  "R$23,25", "3,0", "R$7,67",   "Escalar"],
            ["Shopping Portfólio Geral","R$29,84", "0,1", "R$504,11", "NEGATIVAR imediatamente"],
        ],
        col_widths=[60, 22, 16, 22, 70],
        highlight_col=3,
    )
    pdf.note("Mesmo termo, produto diferente sendo exibido. Negativar no Portfólio Geral — zero risco, conversões concentradas no Best Sellers.")

    # ── 7. LANÇAMENTOS ───────────────────────────────────────────────────────────
    pdf.section_title("7. Lançamentos iminentes — ação necessária hoje")

    pdf.sub_title("Este mês — Sérum Roll on Adeus Olheiras (Impacto G)")
    pdf.table(
        ["Keyword", "Match", "Grupo"],
        [
            ["[roll on olheiras kokeshi]",   "EXACT", "Search Institucional bd"],
            ["[serum roll on olheiras]",      "EXACT", "Search | Exata | Adeus Olheiras"],
            ["[roll on para olheiras]",       "EXACT", "Search | Exata | Adeus Olheiras"],
            ["[serum para olheiras coreano]", "EXACT", "Search Soluções nbd"],
        ],
        col_widths=[72, 20, 98],
    )
    pdf.note("Produto no feed Shopping → priorizar no Best Sellers antes do lançamento.")

    pdf.sub_title("Maio/2026 — 4 lançamentos simultâneos (~7 dias)")
    pdf.table(
        ["Produto", "Impacto", "Keywords-semente"],
        [
            ["Creme Antioleosidade",   "G", "[creme antioleosidade kokeshi], [hidratante antioleosidade coreano]"],
            ["Creme Antissinais",       "G", "[creme antissinais pele de porcelana], [creme antienvelhecimento coreano]"],
            ["Bastão Adeus Poros",      "G", "[bastão adeus poros], [bastão para poros abertos]"],
            ["Dia das Mães",            "M", "[kit presente dia das mães kokeshi], [presente skincare dia das mães]"],
        ],
        col_widths=[52, 16, 122],
    )
    pdf.note("Impacto G: criar grupo dedicado agora + feed Shopping atualizado antes do lançamento.")

    # ── 8. NOVA KEYWORD ──────────────────────────────────────────────────────────
    pdf.section_title("8. Nova keyword sugerida (Search Console)")
    pdf.table(
        ["Keyword", "Match", "Intenção", "Grupo", "Impr. SC", "Posição"],
        [
            ["[perfume cheiro de rica]", "EXACT", "COMPRADOR",
             "Search | Exata | Cheiro De Rica", "333", "8,06"],
        ],
        col_widths=[46, 16, 22, 60, 20, 18],
    )
    pdf.note(
        "Novas regras de sugestão (threshold 100 impressões + intent COMPRADOR) ainda não aplicadas — "
        "CSVs precisam ser regenerados para surfacar keywords dos lançamentos de maio.\n"
        "Rodar: python run_campaign_constraints_analysis.py → python export_google_ads_search_terms.py "
        "→ python run_paid_organic_analysis.py"
    )

    # ── 9. 5 AÇÕES PRIORITÁRIAS ──────────────────────────────────────────────────
    pdf.section_title("9. 5 ações para hoje")
    pdf.table(
        ["#", "Ação", "Impacto", "Risco", "Conf."],
        [
            ["1", "Criar keywords Sérum Roll on Adeus Olheiras + produto no Shopping",
             "Cobertura no lançamento este mês", "Baixo", "95%"],
            ["2", "Negativar 'produtos coreanos para pele' em Search Soluções",
             "Elimina CPA R$360, libera R$54", "Muito baixo", "98%"],
            ["3", "Negativar 'kit pele de porcelana' no Portfólio Geral",
             "Elimina CPA R$504, mantém conv no Best Sellers", "Baixo", "95%"],
            ["4", "Negativar 'creamy' no Shopping Best Sellers",
             "Elimina CPA R$60, libera R$60", "Muito baixo", "92%"],
            ["5", "Reduzir tROAS-alvo 10-15% em branded com ROAS >25x",
             "+R$40.738 receita potencial", "Médio — monitorar CPA", "82%"],
        ],
        col_widths=[8, 68, 56, 32, 16],
    )

    # ── RODAPÉ FINAL ─────────────────────────────────────────────────────────────
    pdf.ln(4)
    pdf.set_font("Arial", "I", 8)
    pdf.set_text_color(*pdf.GRAY)
    pdf.multi_cell(
        0, 5,
        "Fonte dos dados: Google Ads API (últimos 30 dias) + Google Search Console. "
        "Ticket médio utilizado: R$90,00. CPA-limite saudável: R$20 (ótimo) / R$40 (crítico) / R$50 (inviável). "
        "Upside de escala calculado sobre terms com CPA ≤R$15 e ≥2 conversões a +50% de spend ao CPA médio da conta.",
        align="C",
    )

    out = "Kokeshi_Google_Ads_Report_2026-04-24.pdf"
    pdf.output(out)
    print(f"PDF gerado: {out}")
    return out


if __name__ == "__main__":
    build_pdf()
