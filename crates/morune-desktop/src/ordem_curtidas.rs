//! Ordem propria das Musicas curtidas, que o Spotify nao tem.
//!
//! O Spotify guarda as curtidas so na ordem em que foram curtidas, e nao aceita
//! outra. A ordem que o Felipe monta arrastando fica aqui, num arquivo do
//! Morune: no celular a lista continua como o Spotify mostra.
//!
//! O arquivo guarda so ids. Quem decide o que esta curtido continua sendo o
//! Spotify: curtida nova entra no topo, na ordem do Spotify, e a que foi
//! descurtida em outro lugar some sem mexer no resto.
//!
//! **Nova e pela data, nao pelo id.** Descurtir e curtir de novo no celular
//! devolve o mesmo id: olhando so o id, a faixa ficava no lugar antigo do
//! arquivo (a 371a de 727, no caso que achou isto) e parecia nao estar na
//! lista. Curtida com data depois da ultima gravacao da ordem conta como nova.

use std::collections::HashSet;
use std::path::{Path, PathBuf};
use std::time::{SystemTime, UNIX_EPOCH};

use morune_core::TrackId;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Default, PartialEq, Serialize, Deserialize)]
pub struct OrdemCurtidas {
    ids: Vec<TrackId>,
    /// Quando a ordem foi montada (segundos desde 1970). Curtida com data
    /// posterior e nova, mesmo que o id ja esteja em `ids`. Arquivo antigo,
    /// sem o campo, usa a data do proprio arquivo (ver [`ler`]).
    #[serde(default)]
    gravada_em: u64,
    /// A ultima lista de curtidas que veio do Spotify, com a data de cada uma.
    /// Arrastar usa esta, e nao um pedido novo: gravar a ordem nao pode
    /// depender da conexao.
    #[serde(skip)]
    conhecidas: Vec<Curtida>,
}

/// Uma curtida como o Spotify a da: id e instante da curtida.
pub type Curtida = (TrackId, u64);

fn agora() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_secs())
        .unwrap_or(0)
}

impl OrdemCurtidas {
    /// `true` enquanto ninguem arrastou nada: a lista e a do Spotify.
    pub fn vazia(&self) -> bool {
        self.ids.is_empty()
    }

    /// Guarda a lista que acabou de vir do Spotify.
    pub fn lembrar(&mut self, atuais: &[Curtida]) {
        self.conhecidas = atuais.to_vec();
    }

    pub fn conhecidas(&self) -> &[Curtida] {
        &self.conhecidas
    }

    /// A lista do Spotify (`atuais`, mais recente primeiro) na ordem do
    /// usuario. As curtidas feitas depois da ordem vem no topo, na ordem do
    /// Spotify; as outras, no lugar que o usuario deu.
    pub fn aplicar(&self, atuais: &[Curtida]) -> Vec<TrackId> {
        let antigas: HashSet<&TrackId> = atuais
            .iter()
            .filter(|(_, quando)| *quando <= self.gravada_em)
            .map(|(id, _)| id)
            .collect();
        let arrumadas: HashSet<&TrackId> =
            self.ids.iter().filter(|id| antigas.contains(id)).collect();
        atuais
            .iter()
            .map(|(id, _)| id)
            .filter(|id| !arrumadas.contains(id))
            .chain(self.ids.iter().filter(|id| arrumadas.contains(id)))
            .cloned()
            .collect()
    }

    /// Leva `id` para a posicao `para` da lista ja ordenada. A ordem inteira
    /// passa a valer, inclusive as novas que estavam no topo sem lugar fixo.
    pub fn mover(&mut self, atuais: &[Curtida], id: &TrackId, para: usize) -> bool {
        let mut lista = self.aplicar(atuais);
        let Some(de) = lista.iter().position(|item| item == id) else {
            return false;
        };
        let item = lista.remove(de);
        lista.insert(para.min(lista.len()), item);
        self.ids = lista;
        // A ordem agora cobre todas as curtidas que existem: so as de depois
        // deste instante sobem sozinhas. Nunca volta no tempo, para que um
        // relogio atrasado nao transforme curtidas arrumadas em novas.
        let mais_nova = atuais.iter().map(|(_, quando)| *quando).max().unwrap_or(0);
        self.gravada_em = self.gravada_em.max(agora()).max(mais_nova);
        true
    }

    /// Descurtida: sai do arquivo, para que curtir de novo a traga ao topo e
    /// nao ao lugar antigo.
    pub fn esquecer(&mut self, id: &TrackId) -> bool {
        let antes = self.ids.len();
        self.ids.retain(|item| item != id);
        self.ids.len() != antes
    }
}

pub fn arquivo(pasta_dados: &Path) -> PathBuf {
    pasta_dados.join("ordem-curtidas.json")
}

pub fn ler(pasta_dados: &Path) -> OrdemCurtidas {
    let caminho = arquivo(pasta_dados);
    let Ok(texto) = std::fs::read_to_string(&caminho) else {
        return OrdemCurtidas::default();
    };
    let mut ordem: OrdemCurtidas = serde_json::from_str(&texto).unwrap_or_else(|error| {
        tracing::warn!(%error, "ordem das curtidas ilegivel; ignorada");
        OrdemCurtidas::default()
    });
    // Arquivo de antes da data: a ultima escrita dele e quando a ordem foi
    // montada (o arquivo so e escrito ao arrastar ou descurtir).
    if ordem.gravada_em == 0 && !ordem.ids.is_empty() {
        ordem.gravada_em = std::fs::metadata(&caminho)
            .and_then(|m| m.modified())
            .ok()
            .and_then(|t| t.duration_since(UNIX_EPOCH).ok())
            .map(|d| d.as_secs())
            .unwrap_or(0);
    }
    ordem
}

/// Grava num arquivo temporario e troca: queda no meio nao deixa meio arquivo.
pub fn gravar(pasta_dados: &Path, ordem: &OrdemCurtidas) {
    let destino = arquivo(pasta_dados);
    let temp = destino.with_extension("json.tmp");
    let resultado = serde_json::to_vec(ordem)
        .map_err(std::io::Error::other)
        .and_then(|bytes| std::fs::write(&temp, bytes))
        .and_then(|_| std::fs::rename(&temp, &destino));
    if let Err(error) = resultado {
        tracing::warn!(%error, "nao foi possivel gravar a ordem das curtidas");
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn ids(nomes: &[&str]) -> Vec<TrackId> {
        nomes.iter().map(|n| TrackId::spotify(*n)).collect()
    }

    /// Curtidas com datas antigas (antes de qualquer `mover` nos testes), a
    /// primeira a mais recente, como o Spotify entrega.
    fn curtidas(nomes: &[&str]) -> Vec<Curtida> {
        let n = nomes.len() as u64;
        nomes
            .iter()
            .enumerate()
            .map(|(i, nome)| (TrackId::spotify(*nome), 1_000 + n - i as u64))
            .collect()
    }

    /// "b" foi descurtida e curtida de novo no celular: mesmo id, data nova.
    fn com_b_refeita(ordem: &OrdemCurtidas) -> Vec<Curtida> {
        vec![
            (TrackId::spotify("b"), ordem.gravada_em + 60),
            (TrackId::spotify("c"), 1_003),
            (TrackId::spotify("a"), 1_001),
        ]
    }

    #[test]
    fn curtida_refeita_depois_da_ordem_volta_ao_topo() {
        let mut ordem = OrdemCurtidas::default();
        ordem.mover(&curtidas(&["c", "b", "a"]), &TrackId::spotify("a"), 0);
        let atuais = com_b_refeita(&ordem);
        assert_eq!(ordem.aplicar(&atuais), ids(&["b", "a", "c"]));
    }

    #[test]
    fn arrastar_a_refeita_fixa_o_lugar_dela() {
        let mut ordem = OrdemCurtidas::default();
        ordem.mover(&curtidas(&["c", "b", "a"]), &TrackId::spotify("a"), 0);
        let atuais = com_b_refeita(&ordem);
        assert!(ordem.mover(&atuais, &TrackId::spotify("b"), 2));
        assert_eq!(ordem.aplicar(&atuais), ids(&["a", "c", "b"]));
    }

    #[test]
    fn arquivo_antigo_sem_data_usa_a_data_do_arquivo() {
        let pasta =
            std::env::temp_dir().join(format!("morune-ordem-antiga-{}", std::process::id()));
        std::fs::create_dir_all(&pasta).unwrap();
        let ordem = OrdemCurtidas {
            ids: ids(&["a"]),
            ..Default::default()
        };
        std::fs::write(arquivo(&pasta), serde_json::to_vec(&ordem).unwrap()).unwrap();
        let lida = ler(&pasta);
        assert!(lida.gravada_em > 1_700_000_000, "{}", lida.gravada_em);
        let _ = std::fs::remove_dir_all(&pasta);
    }

    #[test]
    fn sem_arrastar_a_lista_e_a_do_spotify() {
        let ordem = OrdemCurtidas::default();
        assert_eq!(
            ordem.aplicar(&curtidas(&["c", "b", "a"])),
            ids(&["c", "b", "a"])
        );
    }

    #[test]
    fn arrastar_fixa_a_ordem_inteira() {
        let mut ordem = OrdemCurtidas::default();
        assert!(ordem.mover(&curtidas(&["c", "b", "a"]), &TrackId::spotify("a"), 0));
        assert_eq!(
            ordem.aplicar(&curtidas(&["c", "b", "a"])),
            ids(&["a", "c", "b"])
        );
    }

    #[test]
    fn curtida_nova_entra_no_topo_sem_mexer_no_resto() {
        let mut ordem = OrdemCurtidas::default();
        ordem.mover(&curtidas(&["c", "b", "a"]), &TrackId::spotify("a"), 0);
        assert_eq!(
            ordem.aplicar(&curtidas(&["e", "d", "c", "b", "a"])),
            ids(&["e", "d", "a", "c", "b"])
        );
    }

    #[test]
    fn descurtida_em_outro_lugar_some_sem_mexer_no_resto() {
        let mut ordem = OrdemCurtidas::default();
        ordem.mover(&curtidas(&["c", "b", "a"]), &TrackId::spotify("a"), 0);
        assert_eq!(ordem.aplicar(&curtidas(&["b", "a"])), ids(&["a", "b"]));
    }

    #[test]
    fn descurtir_e_curtir_de_novo_volta_ao_topo() {
        let mut ordem = OrdemCurtidas::default();
        ordem.mover(&curtidas(&["c", "b", "a"]), &TrackId::spotify("c"), 2);
        assert!(ordem.esquecer(&TrackId::spotify("c")));
        assert_eq!(
            ordem.aplicar(&curtidas(&["c", "b", "a"])),
            ids(&["c", "b", "a"])
        );
    }

    #[test]
    fn grava_e_le_de_volta() {
        let pasta = std::env::temp_dir().join(format!("morune-ordem-{}", std::process::id()));
        std::fs::create_dir_all(&pasta).unwrap();
        let mut ordem = OrdemCurtidas::default();
        ordem.mover(&curtidas(&["b", "a"]), &TrackId::spotify("a"), 0);
        gravar(&pasta, &ordem);
        assert_eq!(ler(&pasta), ordem);
        let _ = std::fs::remove_dir_all(&pasta);
    }
}
